#!/usr/bin/env python3
"""Hook PreToolUse: no deja que el espacio se deforme mientras se trabaja.

  - Write de un archivo NUEVO fuera de la arquitectura (suelto en la raíz, en
    una carpeta no registrada, entregable sin <DD-mmm-YYYY>/<categoria>/,
    nombre con espacios o acentos) → se niega, con la ruta que corresponde.
    Editar archivos que ya existen no se bloquea.
  - Bash o PowerShell que mueva o renombre archivos (mv, git mv, Move-Item,
    Rename-Item, ren, move, ordenar.py --aplicar) → «ask»: Claude Code le pide
    confirmación a la persona antes de ejecutar. Mover siempre se confirma.

Si la persona pidió explícitamente una ubicación nueva, la vía es registrarla
como carpeta con primeros-pasos (Ampliar), no saltarse el hook.
Cualquier error se traga: el hook nunca rompe la sesión.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun  # noqa: E402
import ordenar  # noqa: E402

MOVER = re.compile(r"(^|[\s;&|(])(mv|git\s+mv|move-item|rename-item|ren|rename|move|robocopy\s.*\/mov)\b"
                   r"|ordenar\.py\b[^\n]*--aplicar", re.I)


def responder(decision: str, motivo: str) -> None:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                             "permissionDecision": decision,
                                             "permissionDecisionReason": motivo}}, ensure_ascii=False))


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0
    herramienta = payload.get("tool_name", "")
    entrada = payload.get("tool_input") or {}
    raiz = comun.encontrar_raiz()
    cfg = comun.leer_config(raiz)
    if cfg is None:
        return 0
    if herramienta in ("Bash", "PowerShell"):
        cmd = entrada.get("command", "")
        if MOVER.search(cmd):
            responder("ask", "Este comando mueve o renombra archivos del espacio de trabajo: la persona "
                             "debe confirmarlo. Antes, muéstrale qué se mueve, de dónde y a dónde.")
        return 0
    if herramienta != "Write":
        return 0
    ruta = Path(entrada.get("file_path", ""))
    if not ruta.is_absolute():
        ruta = raiz / ruta
    try:
        rel = ruta.resolve().relative_to(raiz).as_posix()
    except ValueError:
        return 0  # fuera del espacio (scratchpad, temporales): no es asunto de este hook
    if ruta.exists():
        return 0
    motivo = ordenar.evaluar(raiz, cfg, rel)
    if not motivo:
        return 0
    sugerido, por_que = ordenar.destino(raiz, cfg, rel, motivo)
    responder("deny", f"'{rel}' rompe la arquitectura del espacio ({motivo}). "
                      + (f"Escríbelo en '{sugerido}' ({por_que}). " if sugerido else "")
                      + "Mapa de carpetas en CLAUDE.md y docs/espacio-de-trabajo/carpetas.md. Si la persona "
                        "pidió esa ubicación a propósito, regístrala con primeros-pasos (Ampliar) antes de escribir.")
    return 0


if __name__ == "__main__":
    comun.utf8()
    try:
        sys.exit(main())
    except Exception:  # noqa: BLE001
        sys.exit(0)
