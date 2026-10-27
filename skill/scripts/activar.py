#!/usr/bin/env python3
"""Hook UserPromptSubmit: cuando la persona escribe «empezar», «iniciar»,
«configurar», «primeros pasos» o algo equivalente, le indica a Claude que
invoque el skill primeros-pasos. Así se activa siempre, sin depender de que
Claude reconozca la intención.

Solo dispara con mensajes que son eso y nada más («empezar», «configura mi
espacio», «iniciemos») o con frases inequívocas («primeros pasos», «soy nuevo
en el proyecto», «repara mi espacio»). «Configura el linter» no dispara.

    (como hook)       lee el JSON del evento por stdin
    --probar "texto"  dice si ese texto activaría el skill
    --registrar       agrega este hook a .claude/settings.json (lo usan los
                      instaladores, antes de que exista el espacio)

Nunca bloquea: siempre sale con código 0.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun  # noqa: E402

VERBOS = (r"empezar|empecemos|empieza|empiezo|empezamos|iniciar|iniciemos|inicia|inicio|iniciamos|"
          r"comenzar|comencemos|comienza|comienzo|arrancar|arranquemos|arranca|arranco|"
          r"configurar|configuremos|configura|configurame|configuralo|preparar|preparemos|prepara|"
          r"preparame|montar|montemos|monta|instalar|instalemos|setup|onboarding|start|empezar a trabajar")
OBJETO = (r"(mi|el|este|esta|nuestro|nuestra|tu|un|una)\s+(espacio(\s+de\s+trabajo)?|repositorio|repo|"
          r"proyecto|entorno|area(\s+de\s+trabajo)?|carpeta|workspace)")
SOLO = re.compile(rf"^(hola\s+|bueno\s+|ok\s+|vamos\s+a\s+|quiero\s+|necesito\s+|puedes\s+|podemos\s+)*"
                  rf"({VERBOS})(\s+{OBJETO})?(\s+por\s+favor)?$")
FRASES = re.compile(r"\b(primeros\s+pasos|primer\s+paso|configura(r)?\s+mi\s+espacio|prepara(r)?\s+(este|mi)\s+"
                    r"(repositorio|repo|espacio)|soy\s+nuev[oa]\s+en\s+(el|este)\s+(proyecto|equipo|repositorio)|"
                    r"repara(r)?\s+mi\s+espacio|organiza(r)?\s+mis\s+carpetas|ordena(r)?\s+mis\s+carpetas|"
                    r"tengo\s+un\s+proyecto\s+nuevo|cambio\s+mi\s+cargo|ahora\s+tambien\s+hago|"
                    r"(revisa|revisar|audita|auditar|valida|validar)\s+(mis|los|las|todos\s+los)\s+"
                    r"(skills|habilidades))\b")


def normalizar(texto: str) -> str:
    t = comun.sin_acentos(texto or "").lower()
    t = re.sub(r"[¡!¿?.,;:\"'«»()\-_/]+", " ", t)
    return " ".join(t.split())


def activa(texto: str) -> bool:
    t = normalizar(texto)
    if not t or len(t) > 300:
        return False
    return bool(SOLO.match(t) or FRASES.search(t))


def comando(raiz: Path) -> str:
    return f'{comun.python_cmd()} "$CLAUDE_PROJECT_DIR/{comun.skill_rel(raiz)}/scripts/activar.py"'


def registrar(raiz: Path) -> str:
    p = raiz / ".claude" / "settings.json"
    try:
        actual = json.loads(p.read_text(encoding="utf-8") or "{}") if p.is_file() else {}
    except ValueError:
        return "error: .claude/settings.json no es JSON válido; no se tocó"
    grupos = actual.setdefault("hooks", {}).setdefault("UserPromptSubmit", [])
    if "activar.py" in json.dumps(grupos):
        return "ya existía"
    grupos.append({"hooks": [{"type": "command", "command": comando(raiz), "timeout": 10}]})
    comun.escribir(p, json.dumps(actual, ensure_ascii=False, indent=2) + "\n")
    return "registrado"


def main(argv=None) -> int:
    comun.utf8()
    ap = argparse.ArgumentParser(description="Activa primeros-pasos con palabras como «empezar»")
    ap.add_argument("--raiz")
    ap.add_argument("--probar")
    ap.add_argument("--registrar", action="store_true")
    a = ap.parse_args(argv)
    if a.registrar:
        print(f"Activación con «empezar»: {registrar(comun.encontrar_raiz(a.raiz))}")
        return 0
    if a.probar is not None:
        print("activa" if activa(a.probar) else "no activa")
        return 0
    try:
        evento = json.load(sys.stdin) if not sys.stdin.isatty() else {}
    except ValueError:
        return 0
    texto = evento.get("prompt", "") if isinstance(evento, dict) else ""
    if activa(texto):
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": f"La persona escribió «{texto.strip()[:80]}»: quiere empezar, configurar o "
                                 "ajustar su espacio de trabajo. Invoca ahora el skill primeros-pasos con la "
                                 "herramienta Skill y sigue sus pasos."}}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
