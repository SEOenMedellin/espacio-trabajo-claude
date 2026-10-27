#!/usr/bin/env python3
"""Programas para trabajar: los de base (Git, Python, Node.js y Playwright) y los
que la investigación del rol sumó en espacio.json → programas.

    (sin argumentos)      estado de cada programa: OK o FALTA
    --json
    --comando NOMBRE      imprime la orden de instalación para este sistema
    --instalar NOMBRE     la ejecuta. Claude solo la corre después de que la
                          persona diga que sí en la conversación.

Instala con el gestor del sistema (winget en Windows, Homebrew en macOS, apt o
dnf en Linux). Si no hay gestor, da la página oficial de descarga.

Código de salida: 0 todo instalado, 1 falta algo, 2 programa desconocido o
sin forma de instalarlo aquí.
"""
from __future__ import annotations

import argparse
import json
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun  # noqa: E402

BASE = [
    {"nombre": "git", "titulo": "Git", "para": "Historial de versiones y, en Windows, la consola que usan los hooks",
     "descarga": "https://git-scm.com/downloads",
     "winget": "winget install -e --id Git.Git --accept-package-agreements --accept-source-agreements",
     "brew": "brew install git", "apt": "sudo apt-get install -y git", "dnf": "sudo dnf install -y git"},
    {"nombre": "python", "titulo": "Python 3.10+", "para": "Los scripts del espacio de trabajo",
     "descarga": "https://www.python.org/downloads/",
     "winget": "winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements",
     "brew": "brew install python@3.12", "apt": "sudo apt-get install -y python3", "dnf": "sudo dnf install -y python3"},
    {"nombre": "node", "titulo": "Node.js 18+", "para": "Herramientas de JavaScript y Playwright",
     "descarga": "https://nodejs.org/",
     "winget": "winget install -e --id OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements",
     "brew": "brew install node", "apt": "sudo apt-get install -y nodejs npm", "dnf": "sudo dnf install -y nodejs npm"},
    {"nombre": "playwright", "titulo": "Playwright", "para": "Navegador automatizado para investigar y probar páginas",
     "descarga": "https://playwright.dev/docs/intro", "requiere": "node",
     "todos": "npm install -g playwright && npx playwright install chromium"},
]


def _version(cmd: list[str]) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return ""
    return (r.stdout + r.stderr).strip() if r.returncode == 0 else ""


def instalado(nombre: str) -> bool:
    if nombre == "git":
        return shutil.which("git") is not None
    if nombre == "python":
        return sys.version_info >= (3, 10)
    if nombre == "node":
        m = re.search(r"v(\d+)", _version(["node", "--version"])) if shutil.which("node") else None
        return bool(m) and int(m.group(1)) >= 18
    if nombre == "playwright":
        return shutil.which("playwright") is not None
    return False


def gestor() -> str | None:
    sistema = platform.system()
    if sistema == "Windows":
        return "winget" if shutil.which("winget") else None
    if sistema == "Darwin":
        return "brew" if shutil.which("brew") else None
    for g in ("apt", "dnf"):
        if shutil.which("apt-get" if g == "apt" else g):
            return g
    return None


def comando(p: dict) -> str | None:
    if p.get("todos"):
        return p["todos"]
    g = gestor()
    return p.get(g) if g else None


def lista(cfg: dict | None) -> list[dict]:
    """Los de base y los del espacio, con su estado."""
    res = []
    for p in BASE:
        res.append(dict(p, ok=instalado(p["nombre"]), comando=comando(p)))
    for p in (cfg or {}).get("programas", []):
        res.append({"nombre": p["nombre"], "titulo": p["nombre"], "para": p.get("para", ""),
                    "descarga": p.get("instalar", ""), "comando": None,
                    "ok": comun.programa_disponible(p.get("comprobar", ""))})
    return res


def faltantes(cfg: dict | None) -> list[str]:
    return [p["titulo"] for p in lista(cfg) if not p["ok"]]


def main(argv=None) -> int:
    comun.utf8()
    ap = argparse.ArgumentParser(description="Programas para trabajar")
    ap.add_argument("--raiz")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--comando")
    ap.add_argument("--instalar")
    a = ap.parse_args(argv)
    cfg = comun.leer_config(comun.encontrar_raiz(a.raiz))
    progs = lista(cfg)
    nombre = a.comando or a.instalar
    if nombre:
        p = next((x for x in progs if x["nombre"].lower() == nombre.lower()), None)
        if p is None:
            print(f"Programa desconocido: {nombre}", file=sys.stderr)
            return 2
        if p["ok"]:
            print(f"{p['titulo']} ya está instalado.")
            return 0
        req = next((x for x in progs if x["nombre"] == p.get("requiere")), None)
        if req and not req["ok"]:
            print(f"Primero hay que instalar {req['titulo']}.", file=sys.stderr)
            return 2
        if not p["comando"]:
            print(f"No hay un instalador automático para {p['titulo']} en este equipo. "
                  f"Descarga oficial: {p['descarga']}", file=sys.stderr)
            return 2
        if a.comando:
            print(p["comando"])
            return 0
        r = subprocess.run(p["comando"], shell=True)
        if r.returncode != 0:
            print(f"La instalación de {p['titulo']} no terminó bien (código {r.returncode}). "
                  f"Alternativa: {p['descarga']}", file=sys.stderr)
            return 1
        print(f"{p['titulo']} instalado. Si no aparece, cierra y vuelve a abrir la terminal y Claude Code.")
        return 0
    if a.json:
        print(json.dumps(progs, ensure_ascii=False, indent=2))
    else:
        for p in progs:
            linea = f"  {'OK' if p['ok'] else 'FALTA':<6} {p['titulo']} — {p['para']}"
            if not p["ok"]:
                linea += f"\n         instalar: {p['comando'] or p['descarga']}"
            print(linea)
    return 0 if all(p["ok"] for p in progs) else 1


if __name__ == "__main__":
    sys.exit(main())
