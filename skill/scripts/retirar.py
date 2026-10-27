#!/usr/bin/env python3
"""Retira el skill primeros-pasos cuando el espacio ya quedó listo, sin tocar
nada de lo que creó (carpetas, CLAUDE.md, memoria, bitácora, atajos, hooks).

    --estado       activo, desactivado o eliminado
    --desactivar   Claude deja de ver el skill y las palabras «empezar»,
                   «configurar»… dejan de abrirlo. Sus herramientas siguen donde
                   están y los hooks siguen funcionando. Se revierte con --reactivar.
    --reactivar    lo vuelve a activar
    --eliminar     traslada las herramientas del día a día (scripts, plantillas y
                   convenciones) a .claude/espacio/, repunta hooks, CLAUDE.md y
                   atajos, y borra la carpeta del skill. Para volver a tenerlo,
                   se reinstala con el comando de una línea.

Claude solo corre --desactivar o --eliminar después de un sí explícito de la
persona. Código de salida: 0 bien, 1 no se pudo, 2 no aplica.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun  # noqa: E402

DESTINO = ".claude/espacio"
APAGADO = "SKILL.md.desactivado"


def estado() -> str:
    if (comun.SKILL / "SKILL.md").is_file():
        return "activo"
    if (comun.SKILL / APAGADO).is_file():
        return "desactivado"
    return "eliminado"


def _settings(raiz: Path) -> tuple[Path, dict]:
    p = raiz / ".claude" / "settings.json"
    try:
        return p, json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}
    except ValueError:
        raise SystemExit("El archivo .claude/settings.json está dañado: corrígelo antes de retirar el skill.")


def quitar_activacion(raiz: Path) -> None:
    p, datos = _settings(raiz)
    grupos = datos.get("hooks", {}).get("UserPromptSubmit")
    if not grupos:
        return
    quedan = [g for g in grupos if "activar.py" not in json.dumps(g)]
    if quedan:
        datos["hooks"]["UserPromptSubmit"] = quedan
    else:
        datos["hooks"].pop("UserPromptSubmit")
    comun.escribir(p, json.dumps(datos, ensure_ascii=False, indent=2) + "\n")


def desactivar(raiz: Path) -> str:
    if estado() != "activo":
        return f"El skill ya está {estado()}."
    (comun.SKILL / "SKILL.md").rename(comun.SKILL / APAGADO)
    quitar_activacion(raiz)
    return ("Listo: el asistente de configuración quedó desactivado. Tu espacio sigue funcionando igual. "
            "Si algún día lo necesitas, pídeme reactivarlo.")


def reactivar(raiz: Path) -> str:
    if estado() != "desactivado":
        return f"El skill está {estado()}: no hay nada que reactivar."
    (comun.SKILL / APAGADO).rename(comun.SKILL / "SKILL.md")
    import activar
    activar.registrar(raiz)
    return "Listo: el asistente de configuración está activo otra vez."


def eliminar(raiz: Path) -> str:
    if estado() == "eliminado":
        return "El skill ya estaba eliminado."
    viejo = comun.skill_rel(raiz)
    destino = raiz / DESTINO
    if destino.exists():
        return f"Ya existe {DESTINO}/: revísalo antes de eliminar el skill."
    shutil.copytree(comun.SKILL, destino, ignore=shutil.ignore_patterns(
        "SKILL.md", APAGADO, "references", "__pycache__"))
    quitar_activacion(raiz)
    cambiados = []
    candidatos = [raiz / ".claude" / "settings.json", raiz / "CLAUDE.md"]
    candidatos += sorted((raiz / ".claude" / "skills").glob("*/SKILL.md")) if (raiz / ".claude" / "skills").is_dir() else []
    candidatos += sorted((raiz / comun.DOCS).glob("*.md")) if (raiz / comun.DOCS).is_dir() else []
    for f in candidatos:
        if not f.is_file() or f.resolve().is_relative_to(comun.SKILL.resolve()):
            continue
        texto = f.read_text(encoding="utf-8")
        if viejo in texto:
            comun.escribir(f, texto.replace(viejo, DESTINO))
            cambiados.append(f.relative_to(raiz).as_posix())
    dentro = comun.SKILL.resolve().is_relative_to(raiz.resolve())
    if dentro:
        shutil.rmtree(comun.SKILL, ignore_errors=True)
    return ("Listo: eliminé el asistente de configuración. Todo lo que armamos sigue igual y sus herramientas "
            f"ahora viven en {DESTINO}/ ({len(cambiados)} archivo(s) actualizados para apuntar allí)."
            + ("" if dentro else f" La carpeta original ({viejo}) está fuera de este repositorio y no la toqué.")
            + " Si algún día quieres ampliarlo o repararlo, se reinstala con el comando de una línea.")


def main(argv=None) -> int:
    comun.utf8()
    ap = argparse.ArgumentParser(description="Desactivar o eliminar el skill primeros-pasos")
    ap.add_argument("--raiz")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--estado", action="store_true")
    g.add_argument("--desactivar", action="store_true")
    g.add_argument("--reactivar", action="store_true")
    g.add_argument("--eliminar", action="store_true")
    a = ap.parse_args(argv)
    raiz = comun.encontrar_raiz(a.raiz)
    if a.estado:
        print(estado())
        return 0
    if comun.leer_config(raiz) is None:
        print("El espacio todavía no está montado: no tiene sentido retirar el skill.", file=sys.stderr)
        return 2
    accion = desactivar if a.desactivar else reactivar if a.reactivar else eliminar
    print(accion(raiz))
    return 0


if __name__ == "__main__":
    sys.exit(main())
