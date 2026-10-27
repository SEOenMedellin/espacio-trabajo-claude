#!/usr/bin/env python3
"""Revisa que el espacio de trabajo esté completo.

Cada pieza sale como OK, FALTA (no existe), DIVERGE (existe pero no coincide
con espacio.json) o AVISO (no bloquea). FALTA y DIVERGE se reparan con
`montar.py` sin argumentos.

    --breve   modo hook SessionStart: registra el inicio de la sesión (para
              cierre_check.py) e imprime una o dos líneas de contexto.
    --json

Código de salida: 0 sano, 1 hay FALTA o DIVERGE, 2 no hay espacio.json.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bitacora  # noqa: E402
import comun  # noqa: E402

PLANTILLA = comun.SKILL / "assets" / "plantilla"


def revisar(raiz: Path, cfg: dict) -> list[tuple[str, str, str]]:
    res = []

    def item(estado, que, detalle=""):
        res.append((estado, que, detalle))

    claude = raiz / "CLAUDE.md"
    if not claude.is_file():
        item("FALTA", "CLAUDE.md")
    elif comun.MARCA_INICIO not in claude.read_text(encoding="utf-8"):
        item("DIVERGE", "CLAUDE.md", "sin el bloque del espacio de trabajo")
    else:
        item("OK", "CLAUDE.md")
    unidades = comun.proyectos(cfg) or [None]
    for proy in unidades:
        r = comun.resolver(cfg, proy)
        for rol in ("contexto", "entregables", "investigacion", "memoria_global", "memoria_proyecto"):
            if r.get(rol):
                d = raiz / comun.base_dir(r[rol])
                item("OK" if d.is_dir() else "FALTA", comun.base_dir(r[rol]) + "/", rol)
        for c in cfg.get("arquitectura", {}).get("carpetas", []):
            ruta = c["ruta"].replace("<proyecto>", proy) if proy else c["ruta"]
            if "<proyecto>" not in ruta:
                d = raiz / comun.base_dir(ruta)
                item("OK" if d.is_dir() else "FALTA", comun.base_dir(ruta) + "/", c.get("para", "")[:50])
    for proy, b in bitacora.todas(raiz, cfg):
        if not b.is_file():
            item("FALTA", b.relative_to(raiz).as_posix())
        else:
            _, errores = bitacora.parsear(b.read_text(encoding="utf-8"))
            item("AVISO" if errores else "OK", b.relative_to(raiz).as_posix(),
                 f"{len(errores)} entrada(s) mal formada(s)" if errores else "")
    glob = cfg.get("rutas", {}).get("memoria_global")
    if glob:
        item("OK" if (raiz / comun.base_dir(glob) / "README.md").is_file() else "FALTA",
             comun.base_dir(glob) + "/README.md")
    for f in sorted((PLANTILLA / "convenciones").glob("*.md")):
        p = raiz / comun.DOCS / f.name
        item("OK" if p.is_file() else "FALTA", f"{comun.DOCS}/{f.name}")
    ejemplo = raiz / "credenciales" / ".env.example"
    if not ejemplo.is_file():
        item("FALTA", "credenciales/.env.example")
    else:
        tiene = set(re.findall(r"^([A-Z][A-Z0-9_]*)=", ejemplo.read_text(encoding="utf-8"), re.M))
        faltan = [c["variable"] for c in cfg.get("credenciales", []) if c["variable"] not in tiene]
        item("DIVERGE" if faltan else "OK", "credenciales/.env.example",
             "faltan: " + ", ".join(faltan) if faltan else "")
    env = raiz / "credenciales" / ".env"
    if env.is_file():
        vacias = re.findall(r"^([A-Z][A-Z0-9_]*)=\s*$", env.read_text(encoding="utf-8"), re.M)
        if vacias:
            item("AVISO", "credenciales/.env", "sin valor: " + ", ".join(vacias))
        else:
            item("OK", "credenciales/.env")
    else:
        item("FALTA", "credenciales/.env")
    gi = raiz / ".gitignore"
    lineas = {l.strip() for l in gi.read_text(encoding="utf-8").splitlines()} if gi.is_file() else set()
    item("OK" if "credenciales/*" in lineas else "DIVERGE", ".gitignore",
         "" if "credenciales/*" in lineas else "las credenciales no están excluidas")
    st = raiz / ".claude" / "settings.json"
    try:
        hk = json.dumps(json.loads(st.read_text(encoding="utf-8")).get("hooks", {})) if st.is_file() else ""
        faltan = [h for h in ("inicio.py", "cierre_check.py", "orden_check.py") if h not in hk]
        item("DIVERGE" if faltan else "OK", ".claude/settings.json",
             "faltan hooks: " + ", ".join(faltan) if faltan else "")
    except ValueError:
        item("DIVERGE", ".claude/settings.json", "JSON inválido")
    item("OK" if (raiz / comun.ESTADO / "grafo.json").is_file() else "AVISO", f"{comun.ESTADO}/grafo.json",
         "" if (raiz / comun.ESTADO / "grafo.json").is_file() else "corre grafo.py --actualizar")
    if not cfg.get("investigacion_rol"):
        item("AVISO", "investigación del rol", "no se ha hecho: amplía el espacio con primeros-pasos")
    for p in cfg.get("programas", []):
        hay = comun.programa_disponible(p.get("comprobar", ""))
        item("OK" if hay else "AVISO", f"programa {p.get('nombre')}",
             "" if hay else "no está instalado (" + (p.get("instalar") or p.get("para", "")) + ")")
    return res


def programas_faltantes(cfg: dict) -> list[str]:
    return [p.get("nombre", "") for p in cfg.get("programas", [])
            if not comun.programa_disponible(p.get("comprobar", ""))]


def main(argv=None) -> int:
    comun.utf8()
    ap = argparse.ArgumentParser(description="Estado del espacio de trabajo")
    ap.add_argument("--raiz")
    ap.add_argument("--breve", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    raiz = comun.encontrar_raiz(a.raiz)
    if a.breve:
        try:
            payload = json.load(sys.stdin) if not sys.stdin.isatty() else {}
        except ValueError:
            payload = {}
        sid = payload.get("session_id") if isinstance(payload, dict) else None
        if sid:
            comun.sesion_guardar(raiz, sid, {"inicio": time.time(), "avisado": False})
    cfg = comun.leer_config(raiz)
    if cfg is None:
        if a.breve:
            print("Este espacio todavía no está preparado: si la persona quiere empezar, usa el skill primeros-pasos.")
        else:
            print("Sin montar: no hay espacio.json. Corre la entrevista de primeros-pasos.")
        return 0 if a.breve else 2
    res = revisar(raiz, cfg)
    malos = [x for x in res if x[0] in ("FALTA", "DIVERGE")]
    if a.breve:
        p = cfg.get("perfil", {})
        print(f"Espacio de trabajo: {p.get('proyecto', '')} · {p.get('cargo', '')}. Antes de cada tarea: "
              f"grafo.py --plan \"<petición>\" (ver CLAUDE.md).")
        if malos:
            print("Faltan piezas del espacio (" + "; ".join(f"{e} {q}" for e, q, _ in malos[:4])
                  + "). Repáralas con primeros-pasos (montar.py) antes de la primera tarea.")
        faltan = programas_faltantes(cfg)
        if faltan:
            print("Faltan programas para trabajar: " + ", ".join(faltan)
                  + ". Antes de una tarea que los necesite, ofrécele a la persona instalarlos (con su confirmación).")
        return 0
    if a.json:
        print(json.dumps([{"estado": e, "que": q, "detalle": d} for e, q, d in res], ensure_ascii=False, indent=2))
    else:
        print(f"Raíz: {raiz}")
        for e, q, d in res:
            print(f"  {e:<8} {q}" + (f"  ({d})" if d else ""))
        print("Resultado: " + (f"{len(malos)} por reparar. Corre montar.py (repara sin sobrescribir)."
                               if malos else "espacio completo."))
    return 1 if malos else 0


if __name__ == "__main__":
    sys.exit(main())
