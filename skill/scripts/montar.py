#!/usr/bin/env python3
"""Monta, amplía o repara el espacio de trabajo a partir de la entrevista.

    --respuestas r.json   montaje nuevo, o ampliación si ya hay espacio.json
                          (el perfil se reemplaza; carpetas, proyectos y
                          credenciales se suman, nunca se quitan)
    (sin --respuestas)    reparación: todo sale de espacio.json
    --dry-run             valida y muestra qué haría, sin escribir
    --actualizar          rehace el bloque de CLAUDE.md y las convenciones
                          con la versión del skill (copia previa en .espacio/respaldos/)

Nunca borra ni mueve archivos del usuario, nunca quita entradas de
.claude/settings.json, nunca escribe valores de credenciales (solo nombres de
variables) y nunca agrega remotos de git.

Cada línea del reporte dice creado, ya existía, mergeado, actualizado, omitido o error.
Código de salida: 0 bien, 1 hubo errores, 2 las respuestas no pasan la validación.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun  # noqa: E402

PLANTILLA = comun.SKILL / "assets" / "plantilla"
VAR = re.compile(r"^[A-Z][A-Z0-9_]*$")
GITIGNORE = ["credenciales/*", "!credenciales/.env.example", ".env", f"{comun.ESTADO}/",
             "respuestas-espacio.json", "__pycache__/"]


class Reporte:
    def __init__(self) -> None:
        self.lineas: list[tuple[str, str, str]] = []

    def __call__(self, estado: str, que: str, detalle: str = "") -> None:
        self.lineas.append((estado, que, detalle))

    def errores(self) -> int:
        return sum(1 for e, _, _ in self.lineas if e == "error")


# ---------------------------------------------------------------- validación

def validar(cfg: dict) -> list[str]:
    err = []
    perfil = cfg.get("perfil", {})
    for campo in ("cargo", "proyecto", "objetivo"):
        if not str(perfil.get(campo, "")).strip():
            err.append(f"perfil.{campo} está vacío")
    if not perfil.get("tareas"):
        err.append("perfil.tareas necesita al menos una tarea habitual")
    arq = cfg.get("arquitectura", {})
    if not arq.get("tipo"):
        err.append("arquitectura.tipo está vacío")
    if arq.get("modo") not in ("unico", "multiproyecto"):
        err.append("arquitectura.modo debe ser 'unico' o 'multiproyecto'")
    rutas = cfg.get("rutas", {})
    for rol in ("contexto", "entregables", "investigacion", "memoria_global", "bitacora_peticiones"):
        if not rutas.get(rol):
            err.append(f"rutas.{rol} está vacío")
    todas = list(rutas.values()) + [c.get("ruta", "") for c in arq.get("carpetas", [])]
    for r in todas:
        if not r:
            continue
        if r.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", r) or ".." in Path(r).parts:
            err.append(f"ruta no permitida (debe ser relativa y dentro del espacio): {r}")
        if r.split("/")[0] in (".claude", ".git", comun.ESTADO):
            err.append(f"ruta reservada: {r}")
        # Cada carpeta debe dejar sitio, dentro de los límites, para lo que
        # cuelga de ella: en entregables, <categoria>/<archivo>; en el resto, una
        # subcarpeta y el archivo.
        ejemplo = r.replace("<proyecto>", "x" * 30).replace("<DD-mmm-YYYY>", "27-sep-2026").rstrip("/")
        if not r.endswith(".md"):
            ejemplo += "/categoria/" + "a" * 40 + ".docx" if r == rutas.get("entregables") else "/sub/" + "a" * 40 + ".docx"
        largo = comun.problema_longitud(Path("."), ejemplo)
        if largo and "ruta completa" not in largo:
            err.append(f"{r}: arquitectura demasiado profunda, no deja sitio para sus archivos ({largo}); "
                       "usa menos niveles o nombres más cortos")
    for c in arq.get("carpetas", []):
        if not c.get("ruta") or not c.get("para"):
            err.append(f"cada carpeta extra necesita 'ruta' y 'para': {c}")
    if arq.get("modo") == "multiproyecto":
        if not cfg.get("proyectos", {}).get("lista"):
            err.append("modo multiproyecto sin proyectos.lista")
        for rol in ("contexto", "entregables", "bitacora_peticiones", "memoria_proyecto"):
            if "<proyecto>" not in rutas.get(rol, ""):
                err.append(f"en multiproyecto, rutas.{rol} debe contener <proyecto>")
        for p in cfg.get("proyectos", {}).get("lista", []):
            if p != comun.slug(p, largo=30):
                err.append(f"nombre de proyecto no válido como carpeta: {p!r} (usa {comun.slug(p, largo=30)!r}; "
                           "minúsculas, guiones y hasta 30 caracteres)")
    for c in cfg.get("credenciales", []):
        if not VAR.match(str(c.get("variable", ""))):
            err.append(f"variable de credencial no válida: {c.get('variable')!r} (MAYUSCULAS_CON_GUION_BAJO)")
        if "valor" in c:
            err.append(f"{c.get('variable')}: las respuestas nunca llevan el valor de una credencial")
    return err


def combinar(viejo: dict, nuevo: dict) -> dict:
    """El perfil y la arquitectura nuevos mandan; carpetas, proyectos y credenciales se suman."""
    res = json.loads(json.dumps(viejo))
    for k in ("perfil", "idioma", "trato", "git"):
        if k in nuevo:
            res[k] = nuevo[k]
    arq_v, arq_n = res.setdefault("arquitectura", {}), nuevo.get("arquitectura", {})
    for k in ("tipo", "modo", "por_que"):
        if k in arq_n:
            arq_v[k] = arq_n[k]
    rutas_c = {c["ruta"]: c for c in arq_v.get("carpetas", [])}
    for c in arq_n.get("carpetas", []):
        rutas_c[c["ruta"]] = c
    arq_v["carpetas"] = list(rutas_c.values())
    res.setdefault("rutas", {}).update(nuevo.get("rutas", {}))
    if nuevo.get("proyectos"):
        p = res.setdefault("proyectos", {"base": nuevo["proyectos"].get("base", "proyectos"), "lista": []})
        for x in nuevo["proyectos"].get("lista", []):
            if x not in p["lista"]:
                p["lista"].append(x)
    creds = {c["variable"]: c for c in res.get("credenciales", [])}
    for c in nuevo.get("credenciales", []):
        creds[c["variable"]] = c
    res["credenciales"] = list(creds.values())
    return res


# ---------------------------------------------------------------- render

def lista_md(xs, vacio="—") -> str:
    if not xs:
        return f"- {vacio}"
    out = []
    for x in xs:
        if isinstance(x, dict):
            txt = x.get("tarea") or x.get("nombre") or json.dumps(x, ensure_ascii=False)
            extra = ", ".join(f"{k}: {v}" for k, v in x.items() if k not in ("tarea", "nombre") and v)
            out.append(f"- {txt}" + (f" ({extra})" if extra else ""))
        else:
            out.append(f"- {x}")
    return "\n".join(out)


def mapa_carpetas(cfg: dict) -> str:
    r = cfg["rutas"]
    filas = ["| Carpeta | Para qué |", "|---|---|",
             f"| `{r['contexto']}` | Documentos del proyecto que se leen antes de trabajar (insumo, no se modifican) |",
             f"| `{r['entregables']}` | Lo que se produce, por fecha y categoría: `<DD-mmm-YYYY>/<categoria>/<archivo>` |",
             f"| `{r['investigacion']}` | Investigaciones profundas con sus fuentes, reutilizables |",
             f"| `{r['memoria_global']}` | Memoria de trabajo que sirve a cualquier proyecto (un nodo por cosa resuelta) |"]
    if r.get("memoria_proyecto"):
        filas.append(f"| `{r['memoria_proyecto']}` | Memoria específica de cada proyecto |")
    filas.append(f"| `{r['bitacora_peticiones']}` | Una entrada por tarea pedida y cómo se resolvió |")
    for c in cfg["arquitectura"].get("carpetas", []):
        filas.append(f"| `{c['ruta']}` | {c['para']} |")
    filas += ["| `credenciales/` | Claves y accesos (`.env`, nunca se versiona ni se pega en el chat) |",
              f"| `{comun.DOCS}/` | Convenciones de este espacio (detalle de cada regla) |",
              "| `.claude/skills/` | Habilidades: las instaladas y las que se creen aquí |"]
    return "\n".join(filas)


def variables(cfg: dict, raiz: Path) -> dict:
    p = cfg["perfil"]
    multi = cfg["arquitectura"]["modo"] == "multiproyecto"
    lista = comun.proyectos(cfg)
    rel = comun.skill_rel(raiz)
    return {
        "PROYECTO": p["proyecto"],
        "CARGO": p["cargo"],
        "AREA": p.get("area") or "—",
        "OBJETIVO": p["objetivo"],
        "DESTINATARIOS": p.get("destinatarios") or "—",
        "CONOCIMIENTOS": lista_md(p.get("conocimientos")),
        "TAREAS": lista_md(p.get("tareas")),
        "HERRAMIENTAS": lista_md(p.get("herramientas")),
        "TRATO": cfg.get("trato") or "Directo y claro; términos técnicos solo si la persona los usa primero.",
        "IDIOMA": cfg.get("idioma", "es"),
        "TIPO": cfg["arquitectura"]["tipo"],
        "POR_QUE": cfg["arquitectura"].get("por_que") or "—",
        "MODO": ("varios proyectos: " + ", ".join(f"`{x}`" for x in lista)
                 + ". Antes de cada tarea, elegir el proyecto según la petición; si no es evidente, preguntar.")
        if multi else "un solo proyecto.",
        "PROYECTO_FLAG": " --proyecto <proyecto>" if multi else "",
        "MAPA": mapa_carpetas(cfg),
        "CONTEXTO": cfg["rutas"]["contexto"],
        "ENTREGABLES": cfg["rutas"]["entregables"],
        "INVESTIGACION": cfg["rutas"]["investigacion"],
        "MEMORIA_GLOBAL": cfg["rutas"]["memoria_global"],
        "MEMORIA_PROYECTO": cfg["rutas"].get("memoria_proyecto") or cfg["rutas"]["memoria_global"],
        "BITACORA": cfg["rutas"]["bitacora_peticiones"],
        "CREDENCIALES": lista_md([f"`{c['variable']}` — {c.get('para', '')}" for c in cfg.get("credenciales", [])],
                                 "Ninguna por ahora"),
        "PY": comun.python_cmd(),
        "SKILL_REL": rel,
        "DOCS": comun.DOCS,
        "FECHA": comun.hoy(),
        "VERSION": comun.VERSION,
    }


def render(texto: str, v: dict) -> str:
    return re.sub(r"\{\{([A-Z_]+)\}\}", lambda m: str(v.get(m.group(1), m.group(0))), texto)


# ---------------------------------------------------------------- acciones

def asegurar_dir(raiz: Path, rel: str, rep: Reporte, seco: bool) -> None:
    d = raiz / comun.base_dir(rel)
    if d == raiz:
        return
    if d.is_dir():
        rep("ya existía", d.relative_to(raiz).as_posix() + "/")
        return
    if not seco:
        d.mkdir(parents=True, exist_ok=True)
        (d / ".gitkeep").touch()
    rep("creado", d.relative_to(raiz).as_posix() + "/")


def crear_si_falta(p: Path, texto: str, raiz: Path, rep: Reporte, seco: bool) -> None:
    rel = p.relative_to(raiz).as_posix()
    if p.exists():
        rep("ya existía", rel)
        return
    if not seco:
        comun.escribir(p, texto)
    rep("creado", rel)


def respaldar(raiz: Path, p: Path) -> None:
    destino = raiz / comun.ESTADO / "respaldos" / comun.hoy() / p.relative_to(raiz)
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p, destino)


def bloque_claude(raiz: Path, v: dict, rep: Reporte, seco: bool, forzar: bool) -> None:
    p = raiz / "CLAUDE.md"
    bloque = f"{comun.MARCA_INICIO}\n{render((PLANTILLA / 'CLAUDE.md').read_text(encoding='utf-8'), v).strip()}\n{comun.MARCA_FIN}\n"
    if not p.exists():
        if not seco:
            comun.escribir(p, bloque)
        rep("creado", "CLAUDE.md")
        return
    texto = p.read_text(encoding="utf-8")
    if comun.MARCA_INICIO not in texto or comun.MARCA_FIN not in texto:
        if not seco:
            respaldar(raiz, p)
            comun.escribir(p, texto.rstrip("\n") + "\n\n" + bloque)
        rep("mergeado", "CLAUDE.md", "bloque del espacio agregado al final; lo anterior se conserva")
        return
    actual = texto.split(comun.MARCA_INICIO, 1)[1].split(comun.MARCA_FIN, 1)[0]
    nuevo = bloque.split(comun.MARCA_INICIO, 1)[1].split(comun.MARCA_FIN, 1)[0]
    if actual.strip() == nuevo.strip():
        rep("ya existía", "CLAUDE.md")
        return
    if not forzar:
        rep("ya existía", "CLAUDE.md", "el bloque difiere de espacio.json; --actualizar lo rehace")
        return
    if not seco:
        respaldar(raiz, p)
        antes, resto = texto.split(comun.MARCA_INICIO, 1)
        comun.escribir(p, antes + bloque.rstrip("\n") + resto.split(comun.MARCA_FIN, 1)[1])
    rep("actualizado", "CLAUDE.md", f"copia previa en {comun.ESTADO}/respaldos/")


def convenciones(raiz: Path, v: dict, rep: Reporte, seco: bool, forzar: bool) -> None:
    for f in sorted((PLANTILLA / "convenciones").glob("*.md")):
        destino = raiz / comun.DOCS / f.name
        texto = render(f.read_text(encoding="utf-8"), v)
        if destino.exists() and forzar and destino.read_text(encoding="utf-8") != texto:
            if not seco:
                respaldar(raiz, destino)
                comun.escribir(destino, texto)
            rep("actualizado", destino.relative_to(raiz).as_posix())
        else:
            crear_si_falta(destino, texto, raiz, rep, seco)
    perfil = raiz / comun.DOCS / "perfil.md"
    texto = render((PLANTILLA / "perfil.md").read_text(encoding="utf-8"), v)
    if not perfil.exists() or perfil.read_text(encoding="utf-8") != texto:
        existia = perfil.exists()
        if not seco:
            comun.escribir(perfil, texto)
        rep("actualizado" if existia else "creado", perfil.relative_to(raiz).as_posix(),
            "generado desde espacio.json")
    else:
        rep("ya existía", perfil.relative_to(raiz).as_posix())


def credenciales(raiz: Path, cfg: dict, rep: Reporte, seco: bool) -> None:
    base = raiz / "credenciales"
    ejemplo = base / ".env.example"
    cab = render((PLANTILLA / "env.example").read_text(encoding="utf-8"), {})
    deseadas = [(c["variable"], c.get("para", "")) for c in cfg.get("credenciales", [])]
    for p, con_comentario in ((ejemplo, True), (base / ".env", False)):
        existente = p.read_text(encoding="utf-8") if p.exists() else ""
        tiene = set(re.findall(r"^([A-Z][A-Z0-9_]*)=", existente, re.M))
        faltan = [(n, d) for n, d in deseadas if n not in tiene]
        if p.exists() and not faltan:
            rep("ya existía", p.relative_to(raiz).as_posix())
            continue
        lineas = [] if p.exists() else [cab.rstrip("\n") if con_comentario else "# Valores reales. Nunca se versiona ni se pega en el chat."]
        for n, d in faltan:
            lineas += ([f"\n# {d}"] if con_comentario and d else []) + [f"{n}="]
        existia = p.exists()
        if not seco:
            comun.escribir(p, existente.rstrip("\n") + ("\n" if existente else "") + "\n".join(lineas) + "\n")
        rep("mergeado" if existia else "creado", p.relative_to(raiz).as_posix(),
            f"{len(faltan)} variable(s)" if faltan else "")


def gitignore(raiz: Path, rep: Reporte, seco: bool) -> None:
    p = raiz / ".gitignore"
    existente = p.read_text(encoding="utf-8") if p.exists() else ""
    tiene = {l.strip() for l in existente.splitlines()}
    faltan = [l for l in GITIGNORE if l not in tiene]
    if not faltan:
        rep("ya existía", ".gitignore")
        return
    if not seco:
        comun.escribir(p, existente.rstrip("\n") + ("\n\n" if existente else "")
                       + "# --- espacio de trabajo (primeros-pasos) ---\n" + "\n".join(faltan) + "\n")
    rep("mergeado" if existente else "creado", ".gitignore", f"{len(faltan)} línea(s)")


def hooks(raiz: Path, v: dict, rep: Reporte, seco: bool) -> None:
    p = raiz / ".claude" / "settings.json"
    deseado = json.loads(render((PLANTILLA / "settings-hooks.json").read_text(encoding="utf-8"), v))
    if p.exists():
        try:
            actual = json.loads(p.read_text(encoding="utf-8") or "{}")
        except ValueError as e:
            rep("error", ".claude/settings.json", f"JSON inválido ({e}); corrígelo sin quitar entradas y repite")
            return
    else:
        actual = {}
    agregados = []
    hk = actual.setdefault("hooks", {})
    for evento, grupos in deseado["hooks"].items():
        existentes = json.dumps(hk.get(evento, []))
        for g in grupos:
            cmd = g["hooks"][0]["command"]
            marca = cmd.split("/scripts/")[-1].split('"')[0]
            if marca in existentes:
                continue
            hk.setdefault(evento, []).append(g)
            agregados.append(f"{evento}:{marca}")
    if not agregados:
        rep("ya existía", ".claude/settings.json")
        return
    existia = p.exists()
    if not seco:
        comun.escribir(p, json.dumps(actual, ensure_ascii=False, indent=2) + "\n")
    rep("mergeado" if existia else "creado", ".claude/settings.json",
        "agregados: " + ", ".join(agregados) + " (las entradas existentes se conservan)")


def git(raiz: Path, cfg: dict, rep: Reporte, seco: bool) -> None:
    if not cfg.get("git", True):
        rep("omitido", "git", "la persona no quiere historial de versiones")
        return
    if (raiz / ".git").exists():
        rep("ya existía", "git")
        return
    if not shutil.which("git"):
        rep("omitido", "git", "git no está instalado")
        return
    if not seco:
        subprocess.run(["git", "init", "-q"], cwd=raiz, check=False)
    rep("creado", "git", "repositorio local, sin remoto")



def montar(raiz: Path, cfg: dict, seco: bool, forzar: bool, cfg_cambio: bool) -> Reporte:
    rep = Reporte()
    v = variables(cfg, raiz)
    p_cfg = raiz / comun.CONFIG
    if cfg_cambio:
        existia = p_cfg.exists()
        if not seco:
            comun.escribir(p_cfg, json.dumps(cfg, ensure_ascii=False, indent=2) + "\n")
        rep("actualizado" if existia else "creado", comun.CONFIG)
    else:
        rep("ya existía", comun.CONFIG)
    unidades = comun.proyectos(cfg) or [None]
    for proy in unidades:
        r = comun.resolver(cfg, proy)
        for rol in ("contexto", "entregables", "investigacion", "memoria_global", "memoria_proyecto"):
            if r.get(rol):
                asegurar_dir(raiz, r[rol], rep, seco)
        for c in cfg["arquitectura"].get("carpetas", []):
            ruta = c["ruta"].replace("<proyecto>", proy) if proy else c["ruta"]
            if "<proyecto>" not in ruta:
                asegurar_dir(raiz, ruta, rep, seco)
        b = raiz / r["bitacora_peticiones"]
        crear_si_falta(b, render((PLANTILLA / "bitacora-peticiones.md").read_text(encoding="utf-8"),
                                 dict(v, PROYECTO=proy or v["PROYECTO"])), raiz, rep, seco)
    for rol in ("memoria_global", "memoria_proyecto"):
        for proy in unidades:
            r = comun.resolver(cfg, proy).get(rol)
            if r and "<proyecto>" not in r:
                crear_si_falta(raiz / comun.base_dir(r) / "README.md",
                               render((PLANTILLA / "memoria-README.md").read_text(encoding="utf-8"), v),
                               raiz, rep, seco)
    bloque_claude(raiz, v, rep, seco, forzar)
    convenciones(raiz, v, rep, seco, forzar)
    credenciales(raiz, cfg, rep, seco)
    gitignore(raiz, rep, seco)
    hooks(raiz, v, rep, seco)
    git(raiz, cfg, rep, seco)
    if not seco:
        import grafo
        import memoria
        for h in memoria.rebuild(raiz, cfg):
            rep("ejecutado", "memoria.py --rebuild", h)
        rep("ejecutado", "grafo.py --actualizar", grafo.actualizar(raiz, cfg))
    return rep


def main(argv=None) -> int:
    comun.utf8()
    ap = argparse.ArgumentParser(description="Monta o repara el espacio de trabajo")
    ap.add_argument("--raiz")
    ap.add_argument("--respuestas")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--actualizar", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    raiz = comun.encontrar_raiz(a.raiz)
    viejo = comun.leer_config(raiz)
    if a.respuestas:
        p = Path(a.respuestas)
        p = p if p.is_absolute() else raiz / p
        try:
            nuevo = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            print(f"No se pudo leer {p}: {e}", file=sys.stderr)
            return 2
        nuevo.setdefault("version", comun.VERSION)
        nuevo.setdefault("creado", comun.hoy())
        cfg = combinar(viejo, nuevo) if viejo else nuevo
    elif viejo:
        cfg = viejo
    else:
        print("No hay espacio.json ni --respuestas: primero la entrevista de primeros-pasos.", file=sys.stderr)
        return 2
    if a.actualizar:
        cfg["version"] = comun.VERSION
    errores = validar(cfg)
    if errores:
        for e in errores:
            print(f"VALIDACIÓN: {e}", file=sys.stderr)
        return 2
    arq = cfg.setdefault("arquitectura", {})
    if "preexistentes" not in arq:
        # Lo que ya había en la raíz antes del montaje se respeta: ordenar.py y el
        # hook de orden no lo tratan como desorden. Las carpetas de los roles no
        # entran, porque esas sí deben seguir la arquitectura.
        roles = {r.split("/")[0] for r in list(cfg.get("rutas", {}).values())
                 + [c["ruta"] for c in arq.get("carpetas", [])] if r}
        roles.add(cfg.get("proyectos", {}).get("base", "proyectos"))
        omitir = {".git", ".claude", comun.ESTADO, "respuestas-espacio.json", comun.CONFIG, "CLAUDE.md",
                  ".gitignore", "credenciales", "docs"}
        arq["preexistentes"] = sorted(h.name for h in raiz.iterdir() if h.name not in roles | omitir)
    cambio = viejo is None or json.dumps(viejo, sort_keys=True) != json.dumps(cfg, sort_keys=True)
    rep = montar(raiz, cfg, a.dry_run, a.actualizar, cambio)
    if a.respuestas and not a.dry_run and rep.errores() == 0:
        p = Path(a.respuestas)
        p = p if p.is_absolute() else raiz / p
        if p.name == "respuestas-espacio.json":
            p.unlink(missing_ok=True)
    if a.json:
        print(json.dumps([{"estado": e, "que": q, "detalle": d} for e, q, d in rep.lineas], ensure_ascii=False, indent=2))
    else:
        print(("[dry-run] " if a.dry_run else "") + f"Espacio de trabajo en {raiz}")
        for e, q, d in rep.lineas:
            print(f"  {e:<11} {q}" + (f"  ({d})" if d else ""))
        cuenta = {}
        for e, _, _ in rep.lineas:
            cuenta[e] = cuenta.get(e, 0) + 1
        print("Resumen: " + ", ".join(f"{n} {e}" for e, n in cuenta.items()))
    return 1 if rep.errores() else 0


if __name__ == "__main__":
    sys.exit(main())
