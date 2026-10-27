#!/usr/bin/env python3
"""Mantiene la arquitectura del espacio: detecta lo que está fuera de lugar y
propone (o aplica, con confirmación) a dónde va cada archivo.

Qué cuenta como desorden:
  - un archivo o carpeta en la raíz que no pertenece a la arquitectura
    (ni a lo que ya existía antes del montaje: `arquitectura.preexistentes`);
  - en modo multiproyecto, una carpeta bajo la base de proyectos que no es un
    proyecto registrado, o una subcarpeta que no es de un rol;
  - un entregable que no está en `<DD-mmm-YYYY>/<categoria>/`;
  - un nombre con espacios, acentos o mayúsculas en las carpetas de trabajo
    (contexto y lo preexistente se respetan: son documentos de terceros);
  - archivos idénticos (mismo contenido) en dos lugares de trabajo.

El destino se decide por el contenido y el uso: extensión, palabras del nombre
y de las primeras líneas, y fecha de modificación (para el entregable).
Lo que no se puede decidir queda como «revisar con la persona».

Uso (desde la raíz):
    python <skill>/scripts/ordenar.py              plan de reorganización (no mueve nada)
    python <skill>/scripts/ordenar.py --resumen    una línea (la usa inicio.py)
    python <skill>/scripts/ordenar.py --aplicar    mueve lo que tiene destino, según el
                                                   último plan, y actualiza referencias
    python <skill>/scripts/ordenar.py --json

--aplicar solo se corre después de mostrarle el plan a la persona, archivo por
archivo, y recibir su confirmación explícita (con --solo r1,r2 se mueven solo
los que aprobó). Además, el hook orden_check.py hace que Claude Code pida
permiso antes de ejecutarlo.
Nunca sobrescribe: si el destino existe, agrega un sufijo. Registra cada
movimiento solo en .espacio/movimientos.log (registro técnico: no es bitácora
de trabajo y ni el grafo ni la bitácora lo leen).

Código de salida: 0 en orden (o aplicado), 1 hay desorden, 2 no hay espacio.json.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun  # noqa: E402

RAIZ_ARCHIVOS = {"claude.md", "espacio.json", ".gitignore", ".gitattributes", "agents.md",
                 "respuestas-espacio.json", "license", "license.md", "license.txt", "readme.md", "readme",
                 "contributing.md", "changelog.md", ".editorconfig", ".env.example"}
RAIZ_DIRS = {".claude", comun.ESTADO, ".git", ".github", ".vscode", ".idea", "credenciales", "docs"}
FECHA = re.compile(r"^\d{2}-(" + "|".join(comun.MESES) + r")-\d{4}$")
NOMBRE_OK = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
IGNORAR = {".gitkeep", "INDICE.md", "README.md", ".DS_Store", "Thumbs.db", "desktop.ini"}

CATEGORIAS = [  # (categoría, extensiones, palabras)
    ("presentaciones", {".pptx", ".ppt", ".key"}, ("presentacion", "deck", "slides", "pitch")),
    ("informes", {".pdf", ".docx", ".doc", ".html"}, ("informe", "reporte", "report", "diagnostico", "auditoria")),
    ("propuestas", set(), ("propuesta", "cotizacion", "oferta", "licitacion")),
    ("datos", {".csv", ".xlsx", ".xls", ".parquet", ".tsv", ".sqlite"}, ("datos", "export", "dataset")),
    ("codigo", {".py", ".js", ".ts", ".sh", ".ps1", ".sql", ".ipynb", ".r"}, ()),
    ("imagenes", {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}, ()),
    ("documentos", {".md", ".txt", ".odt", ".rtf"}, ()),
]
PALABRAS_CONTEXTO = ("brief", "contrato", "manual", "requisito", "requerimiento", "lineamiento", "guia",
                     "politica", "alcance", "acta-de-inicio", "organigrama", "glosario", "diccionario")
PALABRAS_INVESTIGACION = ("investigacion", "research", "estado-del-arte", "benchmark", "fuentes")


# ---------------------------------------------------------------- reglas

def estructura(raiz: Path, cfg: dict) -> dict:
    """Qué está permitido en el primer nivel y dónde viven los roles."""
    arq = cfg.get("arquitectura", {})
    dirs, archivos = set(RAIZ_DIRS), set(RAIZ_ARCHIVOS)
    for x in arq.get("preexistentes", []):
        (dirs if (raiz / x).is_dir() else archivos).add(x.lower() if not (raiz / x).is_dir() else x)
    multi = arq.get("modo") == "multiproyecto"
    base = cfg.get("proyectos", {}).get("base", "proyectos")
    rutas = [v for v in cfg.get("rutas", {}).values() if v] + [c["ruta"] for c in arq.get("carpetas", [])]
    for r in rutas:
        primero = r.split("/")[0]
        if primero.endswith(".md"):
            archivos.add(primero.lower())
        elif primero != "<proyecto>":
            dirs.add(primero)
    if multi:
        dirs.add(base)
    por_proyecto = set()
    for r in rutas:
        if r.startswith(f"{base}/<proyecto>/"):
            por_proyecto.add(r[len(f"{base}/<proyecto>/"):].split("/")[0])
    return {"dirs": dirs, "archivos": archivos, "multi": multi, "base": base,
            "proyectos": set(comun.proyectos(cfg)), "por_proyecto": por_proyecto}


def entregables_bases(cfg: dict) -> list[str]:
    lista = comun.proyectos(cfg) or [None]
    return [comun.base_dir(comun.resolver(cfg, p)["entregables"]) for p in lista
            if comun.resolver(cfg, p).get("entregables") and "<proyecto>" not in comun.resolver(cfg, p)["entregables"]]


def contexto_bases(cfg: dict) -> list[str]:
    lista = comun.proyectos(cfg) or [None]
    return [comun.base_dir(comun.resolver(cfg, p)["contexto"]) for p in lista
            if comun.resolver(cfg, p).get("contexto") and "<proyecto>" not in comun.resolver(cfg, p)["contexto"]]


def evaluar(raiz: Path, cfg: dict, rel: str, est: dict | None = None, es_dir: bool = False) -> str:
    """'' si la ruta respeta la arquitectura; si no, el motivo."""
    est = est or estructura(raiz, cfg)
    partes = rel.split("/")
    primero = partes[0]
    if primero in (".claude", comun.ESTADO, ".git"):
        return ""
    if primero in est["archivos"] and primero.endswith(".md"):
        return ""
    largo = comun.problema_longitud(raiz, rel)
    if largo:
        return largo
    if primero in [x for x in cfg.get("arquitectura", {}).get("preexistentes", [])]:
        return ""
    if len(partes) == 1 and not es_dir:
        if primero.lower() in est["archivos"]:
            return ""
        return "archivo suelto en la raíz"
    if primero not in est["dirs"]:
        return f"carpeta '{primero}/' no pertenece a la arquitectura"
    if est["multi"] and primero == est["base"] and len(partes) >= 2:
        if partes[1] not in est["proyectos"]:
            return f"'{partes[1]}' no es un proyecto registrado"
        validas = {x for x in est["por_proyecto"] if not x.startswith("<")}
        fecha_directa = any(x.startswith("<") for x in est["por_proyecto"])
        if len(partes) >= 3 and partes[2] not in validas and not (fecha_directa and FECHA.match(partes[2])):
            return (f"'{partes[2]}' no es una carpeta de proyecto (permitidas: {', '.join(sorted(validas))}"
                    + (", <DD-mmm-YYYY>" if fecha_directa else "") + ")")
    for base in entregables_bases(cfg):
        if rel.startswith(base + "/"):
            resto = rel[len(base) + 1:].split("/")
            if resto[0] in est["por_proyecto"] or resto[0] in est["dirs"]:
                continue  # otra carpeta de rol que comparte base con los entregables
            if not FECHA.match(resto[0]) or (len(resto) < 3 and not es_dir):
                return "entregable fuera de <DD-mmm-YYYY>/<categoria>/"
    nombre = partes[-1]
    en_contexto = any(rel.startswith(c + "/") for c in contexto_bases(cfg))
    if not en_contexto and nombre not in IGNORAR and not NOMBRE_OK.match(nombre) and primero not in ("docs", "credenciales"):
        return "nombre con espacios, acentos o mayúsculas"
    return ""


# ---------------------------------------------------------------- destino

def categoria(p: Path) -> str:
    nombre = comun.slug(p.stem)
    ext = p.suffix.lower()
    for cat, exts, palabras in CATEGORIAS:
        if any(w in nombre for w in palabras):
            return cat
    for cat, exts, _ in CATEGORIAS:
        if ext in exts:
            return cat
    return "documentos"


def proyecto_de(rel: str, cfg: dict) -> str | None:
    est_base = cfg.get("proyectos", {}).get("base", "proyectos")
    partes = rel.split("/")
    if len(partes) >= 2 and partes[0] == est_base and partes[1] in comun.proyectos(cfg):
        return partes[1]
    lista = comun.proyectos(cfg)
    return lista[0] if len(lista) == 1 else None


def nombre_limpio(nombre: str) -> str:
    p = Path(nombre)
    return comun.slug(p.stem) + p.suffix.lower()


def destino(raiz: Path, cfg: dict, rel: str, motivo: str) -> tuple[str, str]:
    """(ruta destino o '', por qué)."""
    p = raiz / rel
    proy = proyecto_de(rel, cfg)
    if comun.proyectos(cfg) and proy is None:
        return "", "hay varios proyectos y no se sabe de cuál es: preguntar"
    r = comun.resolver(cfg, proy)
    nombre = nombre_limpio(p.name)
    if motivo.startswith("nombre con"):
        return str(Path(rel).parent.as_posix() + "/" + nombre).lstrip("./"), "renombrar sin espacios ni acentos"
    if motivo.startswith(("ruta demasiado", "nombre demasiado", "la ruta completa")):
        partes = rel.split("/")[:-1]
        base = next((b for b in entregables_bases(cfg) if rel.startswith(b + "/")), "")
        if base:
            resto = rel[len(base) + 1:].split("/")
            fecha = resto[0] if FECHA.match(resto[0]) else comun.hoy()
            cat = comun.slug(resto[1], largo=20) if len(resto) >= 3 else categoria(p)
            corta = f"{base}/{fecha}/{cat}/{nombre}"
        else:
            corta = "/".join(partes[:max(1, comun.MAX_NIVELES - 3)] + [nombre])
        if comun.problema_longitud(raiz, corta):
            return "", "ni acortando el nombre cabe: decidir con la persona una ubicación más corta"
        return corta, "aplanar la ruta y acortar el nombre para que funcione en Windows y macOS"
    texto = ""
    if p.suffix.lower() in (".md", ".txt", ".csv", ".html", ".json"):
        try:
            texto = comun.slug(p.read_text(encoding="utf-8", errors="replace")[:600], largo=10_000)
        except OSError:
            pass
    clave = comun.slug(p.stem) + "-" + texto
    if any(w in clave for w in PALABRAS_CONTEXTO):
        return f"{comun.base_dir(r['contexto'])}/{nombre}", "documento de referencia: va al contexto"
    if any(w in clave for w in PALABRAS_INVESTIGACION):
        return f"{comun.base_dir(r['investigacion'])}/{nombre}", "investigación: va a la carpeta de investigaciones"
    cat = categoria(p)
    if cat == "datos":
        for c in cfg.get("arquitectura", {}).get("carpetas", []):
            ruta = c["ruta"].replace("<proyecto>", proy or "")
            if "crudo" in ruta or ("datos" in ruta and "proces" not in ruta):
                return f"{comun.base_dir(ruta)}/{nombre}", "datos: van a la carpeta de datos"
    fecha = comun.hoy(dt.date.fromtimestamp(p.stat().st_mtime)) if p.exists() else comun.hoy()
    if motivo.startswith("entregable fuera"):
        base = next((b for b in entregables_bases(cfg) if rel.startswith(b + "/")), comun.base_dir(r["entregables"]))
        resto = rel[len(base) + 1:].split("/")
        if FECHA.match(resto[0]):
            fecha = resto[0]
        return f"{base}/{fecha}/{cat}/{nombre}", f"entregable de {fecha}, categoría {cat}"
    if p.is_dir():
        return "", "carpeta fuera de la arquitectura: revisar con la persona (registrarla o repartir su contenido)"
    return f"{comun.base_dir(r['entregables'])}/{fecha}/{cat}/{nombre}", f"producido el {fecha}: entregable de {cat}"


# ---------------------------------------------------------------- escaneo

def escanear(raiz: Path, cfg: dict) -> dict:
    est = estructura(raiz, cfg)
    hallazgos, vistos = [], {}
    for hijo in sorted(raiz.iterdir()):
        rel = hijo.name
        if rel in (".git", comun.ESTADO, ".claude"):
            continue
        motivo = evaluar(raiz, cfg, rel, est, es_dir=hijo.is_dir())
        if motivo:
            d, por = destino(raiz, cfg, rel, motivo)
            hallazgos.append({"ruta": rel + ("/" if hijo.is_dir() else ""), "motivo": motivo, "destino": d, "por_que": por})
            continue
        if not hijo.is_dir() or rel in ("docs", "credenciales") or rel in cfg.get("arquitectura", {}).get("preexistentes", []):
            continue
        for f in sorted(hijo.rglob("*")):
            relf = f.relative_to(raiz).as_posix()
            if "__pycache__" in f.parts or f.name in IGNORAR:
                continue
            motivo = evaluar(raiz, cfg, relf, est, es_dir=f.is_dir())
            if motivo and (f.is_file() or motivo.startswith(("'", "carpeta"))):
                if any(relf.startswith(h["ruta"]) for h in hallazgos if h["ruta"].endswith("/")):
                    continue
                d, por = destino(raiz, cfg, relf, motivo)
                hallazgos.append({"ruta": relf + ("/" if f.is_dir() else ""), "motivo": motivo, "destino": d, "por_que": por})
            if f.is_file() and f.stat().st_size < 20_000_000:
                h = hashlib.sha1(f.read_bytes()).hexdigest()
                vistos.setdefault(h, []).append(relf)
    duplicados = [v for v in vistos.values() if len(v) > 1]
    return {"hallazgos": hallazgos, "duplicados": duplicados}


# ---------------------------------------------------------------- aplicar

def libre(p: Path) -> Path:
    if not p.exists():
        return p
    n = 2
    while (p.parent / f"{p.stem}-{n}{p.suffix}").exists():
        n += 1
    return p.parent / f"{p.stem}-{n}{p.suffix}"


def actualizar_referencias(raiz: Path, movidos: list[tuple[str, str]]) -> int:
    """Reemplaza las rutas viejas por las nuevas en los .md del espacio (no en .claude/skills)."""
    cambios = 0
    for f in raiz.rglob("*.md"):
        rel = f.relative_to(raiz).as_posix()
        if rel.startswith((".claude/skills/", ".git/", comun.ESTADO + "/")):
            continue
        try:
            texto = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        nuevo = texto
        for viejo, actual in movidos:
            nuevo = nuevo.replace(viejo, actual)
        if nuevo != texto:
            comun.escribir(f, nuevo)
            cambios += 1
    return cambios


def aplicar(raiz: Path, solo: set[str] | None = None) -> list[str]:
    plan_p = raiz / comun.ESTADO / "orden-plan.json"
    if not plan_p.is_file():
        return ["No hay plan: corre ordenar.py primero y muéstraselo a la persona."]
    plan = json.loads(plan_p.read_text(encoding="utf-8"))
    movidos, salida = [], []
    for h in plan["hallazgos"]:
        if not h["destino"] or (solo and h["ruta"].rstrip("/") not in solo):
            continue
        origen = raiz / h["ruta"].rstrip("/")
        if not origen.exists():
            continue
        dest = libre(raiz / h["destino"])
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(origen), str(dest))
        par = (h["ruta"].rstrip("/"), dest.relative_to(raiz).as_posix())
        movidos.append(par)
        salida.append(f"movido  {par[0]}  →  {par[1]}")
    if movidos:
        refs = actualizar_referencias(raiz, movidos)
        log = raiz / comun.ESTADO / "movimientos.log"
        with open(log, "a", encoding="utf-8") as fh:
            for a, b in movidos:
                fh.write(f"{dt.datetime.now().isoformat(timespec='seconds')}\t{a}\t{b}\n")
        salida.append(f"referencias actualizadas en {refs} documento(s)")
    plan_p.unlink()
    return salida or ["Nada que mover."]


def main(argv=None) -> int:
    comun.utf8()
    ap = argparse.ArgumentParser(description="Orden del espacio de trabajo")
    ap.add_argument("--raiz")
    ap.add_argument("--aplicar", action="store_true")
    ap.add_argument("--solo", help="con --aplicar: solo estas rutas de origen, separadas por coma")
    ap.add_argument("--resumen", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    raiz = comun.encontrar_raiz(a.raiz)
    cfg = comun.leer_config(raiz)
    if cfg is None:
        print("No hay espacio.json: el espacio no está montado (usa primeros-pasos).", file=sys.stderr)
        return 2
    if a.aplicar:
        solo = {x.strip().rstrip("/") for x in a.solo.split(",")} if a.solo else None
        for l in aplicar(raiz, solo):
            print(l)
        import grafo
        print(grafo.actualizar(raiz, cfg))
        return 0
    res = escanear(raiz, cfg)
    n, d = len(res["hallazgos"]), len(res["duplicados"])
    if a.resumen:
        if n or d:
            print(f"Orden del espacio: {n} elemento(s) fuera de la arquitectura y {d} grupo(s) de duplicados. "
                  "Propón a la persona reorganizarlo (ordenar.py muestra el plan).")
        return 1 if n or d else 0
    comun.escribir(raiz / comun.ESTADO / "orden-plan.json", json.dumps(res, ensure_ascii=False, indent=1))
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        if not (n or d):
            print("El espacio respeta su arquitectura.")
        for h in res["hallazgos"]:
            print(f"• {h['ruta']}  —  {h['motivo']}")
            print(f"    → {h['destino'] or '(revisar con la persona)'}  ({h['por_que']})")
        for grupo in res["duplicados"]:
            print("• Duplicados (mismo contenido): " + ", ".join(grupo))
        if n:
            print("\nPara mover lo que tiene destino, con el sí de la persona: ordenar.py --aplicar")
    return 1 if n or d else 0


if __name__ == "__main__":
    sys.exit(main())
