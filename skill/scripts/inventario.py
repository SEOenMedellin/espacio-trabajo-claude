#!/usr/bin/env python3
"""Inventario de lo que ya trae el repositorio: skills, comandos, agentes,
archivos de reglas (CLAUDE.md, AGENTS.md), hooks y servidores MCP. Es el
punto de partida para revisarlos, validar su conocimiento y adaptarlos al
espacio (references/skills-existentes.md).

No cuenta lo propio: este skill y los atajos que crea.

    (sin argumentos)   resumen legible
    --json             el inventario completo
    --guardar          marca el inventario actual como revisado
    --cambios          qué skills son nuevos o cambiaron desde la última revisión

Código de salida: 0 bien; con --cambios, 1 si hay algo por revisar.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun  # noqa: E402

MARCA_ATAJO = "atajo de primeros-pasos"
TEXTO = {".md", ".py", ".sh", ".ps1", ".js", ".mjs", ".ts", ".json", ".yaml", ".yml", ".toml", ".txt", ".html"}
OMITIR = {".git", "node_modules", ".venv", "venv", "__pycache__", comun.ESTADO, "dist", "build"}
REGLAS = ("CLAUDE.md", "CLAUDE.local.md", "AGENTS.md")


def frontmatter(texto: str) -> dict:
    if not texto.startswith("---"):
        return {}
    partes = texto.split("---", 2)
    if len(partes) < 3:
        return {}
    cab, res = partes[1], {}
    for clave in ("name", "description"):
        m = re.search(rf"^{clave}:\s*(.*?)(?=^\S[\w-]*:|\Z)", cab, re.M | re.S)
        if m:
            res[clave] = " ".join(m.group(1).replace(">-", " ").replace(">", " ").replace("|", " ").split()).strip("'\"")
    return res


def _huella(carpeta: Path) -> str:
    h = hashlib.sha1()
    for f in sorted(x for x in carpeta.rglob("*") if x.is_file() and "__pycache__" not in x.parts):
        h.update(f.relative_to(carpeta).as_posix().encode())
        try:
            h.update(f.read_bytes())
        except OSError:
            pass
    return h.hexdigest()[:16]


def es_propio(carpeta: Path) -> bool:
    if carpeta.resolve() == comun.SKILL.resolve():
        return True
    s = carpeta / "SKILL.md"
    try:
        return MARCA_ATAJO in s.read_text(encoding="utf-8", errors="replace")[:4000]
    except OSError:
        return False


def skills(raiz: Path) -> list[dict]:
    res = []
    base = raiz / ".claude" / "skills"
    for s in sorted(base.glob("*/SKILL.md")) if base.is_dir() else []:
        carpeta = s.parent
        if es_propio(carpeta):
            continue
        texto = s.read_text(encoding="utf-8", errors="replace")
        fm = frontmatter(texto)
        archivos = sorted(f.relative_to(carpeta).as_posix() for f in carpeta.rglob("*")
                          if f.is_file() and "__pycache__" not in f.parts)
        res.append({"nombre": fm.get("name") or carpeta.name, "carpeta": carpeta.name,
                    "ruta": carpeta.relative_to(raiz).as_posix(), "descripcion": fm.get("description", ""),
                    "frontmatter": bool(fm), "archivos": archivos, "huella": _huella(carpeta)})
    return res


def _md_en(carpeta: Path, raiz: Path) -> list[dict]:
    res = []
    for f in sorted(carpeta.glob("*.md")) if carpeta.is_dir() else []:
        fm = frontmatter(f.read_text(encoding="utf-8", errors="replace"))
        res.append({"nombre": fm.get("name") or f.stem, "ruta": f.relative_to(raiz).as_posix(),
                    "descripcion": fm.get("description", "")})
    return res


def archivos_de_reglas(raiz: Path, profundidad: int = 4) -> list[str]:
    res = []

    def bajar(d: Path, nivel: int) -> None:
        for h in sorted(d.iterdir()):
            if h.is_dir():
                if h.name not in OMITIR and nivel < profundidad and not (h / "SKILL.md").exists():
                    bajar(h, nivel + 1)
            elif h.name in REGLAS:
                res.append(h.relative_to(raiz).as_posix())
    bajar(raiz, 0)
    return res


def hooks(raiz: Path) -> list[dict]:
    res = []
    for nombre in ("settings.json", "settings.local.json"):
        p = raiz / ".claude" / nombre
        try:
            datos = json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}
        except ValueError:
            continue
        for evento, grupos in (datos.get("hooks") or {}).items():
            for g in grupos or []:
                for h in g.get("hooks", []):
                    cmd = h.get("command", "")
                    if cmd and comun.SKILL.name not in cmd:
                        res.append({"archivo": f".claude/{nombre}", "evento": evento, "comando": cmd})
    return res


def mcp(raiz: Path) -> list[dict]:
    p = raiz / ".mcp.json"
    try:
        datos = json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}
    except ValueError:
        return [{"nombre": "(.mcp.json inválido)", "comando": ""}]
    return [{"nombre": n, "comando": " ".join([s.get("command", "") or s.get("url", ""), *s.get("args", [])]).strip()}
            for n, s in (datos.get("mcpServers") or {}).items()]


def inventario(raiz: Path) -> dict:
    return {"skills": skills(raiz), "comandos": _md_en(raiz / ".claude" / "commands", raiz),
            "agentes": _md_en(raiz / ".claude" / "agents", raiz), "reglas": archivos_de_reglas(raiz),
            "hooks": hooks(raiz), "mcp": mcp(raiz)}


def _marca(raiz: Path) -> Path:
    return raiz / comun.ESTADO / "inventario.json"


def guardar(raiz: Path) -> None:
    comun.escribir(_marca(raiz), json.dumps({s["ruta"]: s["huella"] for s in skills(raiz)}, indent=2))


def cambios(raiz: Path) -> list[str]:
    """Skills nuevos o modificados desde la última revisión ([] si nunca hubo ninguno que revisar)."""
    try:
        previo = json.loads(_marca(raiz).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        previo = {}
    return [s["nombre"] for s in skills(raiz) if previo.get(s["ruta"]) != s["huella"]]


def main(argv=None) -> int:
    comun.utf8()
    ap = argparse.ArgumentParser(description="Inventario de skills y reglas del repositorio")
    ap.add_argument("--raiz")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--guardar", action="store_true")
    ap.add_argument("--cambios", action="store_true")
    a = ap.parse_args(argv)
    raiz = comun.encontrar_raiz(a.raiz)
    if a.guardar:
        guardar(raiz)
        print("Inventario marcado como revisado.")
        return 0
    if a.cambios:
        c = cambios(raiz)
        print(json.dumps(c, ensure_ascii=False) if a.json else
              ("Por revisar: " + ", ".join(c) if c else "Sin skills nuevos ni cambiados."))
        return 1 if c else 0
    inv = inventario(raiz)
    if a.json:
        print(json.dumps(inv, ensure_ascii=False, indent=2))
        return 0
    print(f"Skills: {len(inv['skills'])}")
    for s in inv["skills"]:
        print(f"  - {s['nombre']} ({s['ruta']}, {len(s['archivos'])} archivos): {s['descripcion'][:120]}")
    for clave, titulo in (("comandos", "Comandos"), ("agentes", "Agentes")):
        if inv[clave]:
            print(f"{titulo}: " + ", ".join(x["nombre"] for x in inv[clave]))
    if inv["reglas"]:
        print("Archivos de reglas: " + ", ".join(inv["reglas"]))
    if inv["hooks"]:
        print(f"Hooks de otros: {len(inv['hooks'])}")
    if inv["mcp"]:
        print("Servidores MCP: " + ", ".join(x["nombre"] for x in inv["mcp"]))
    if not any(inv.values()):
        print("Repositorio sin skills ni reglas previas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
