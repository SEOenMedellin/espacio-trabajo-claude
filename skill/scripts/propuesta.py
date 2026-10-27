#!/usr/bin/env python3
"""Escribe en lenguaje sencillo la propuesta del espacio (SKILL.md, paso 6) a
partir de respuestas-espacio.json, para mostrársela a la persona tal cual y
preguntarle si la aprueba. Así Claude no tiene que redactarla.

    python propuesta.py [--respuestas R]

Código de salida: 0 bien, 2 sin respuestas.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun  # noqa: E402
import programas  # noqa: E402
import revisar  # noqa: E402


def _tarea(t) -> str:
    return t.get("tarea", "") if isinstance(t, dict) else str(t)


def propuesta(resp: dict) -> str:
    p = resp.get("perfil", {})
    arq = resp.get("arquitectura", {})
    rutas = resp.get("rutas", {})
    inv = resp.get("investigacion_rol") or {}
    out = [f"Así va a quedar tu espacio para **{p.get('proyecto', '')}**:", ""]

    out.append(f"**Tus carpetas** ({arq.get('por_que', '').rstrip('.')}):")
    nucleo = [(rutas.get("contexto"), "lo que necesito saber de tu proyecto (documentos, normas, ejemplos)"),
              (rutas.get("entregables"), "lo que entregas, ordenado por fecha"),
              (rutas.get("investigacion"), "lo que investiguemos, con sus fuentes"),
              (rutas.get("memoria_global"), "lo que vayamos aprendiendo")]
    for ruta, para in nucleo + [(c.get("ruta"), c.get("para", "")) for c in arq.get("carpetas", [])]:
        if ruta:
            out.append(f"- `{ruta}` — {para}")
    out += ["", f"**Lo que voy a saber de ti:** que eres {p.get('cargo', '')}, que tu objetivo es "
                f"{p.get('objetivo', '').rstrip('.').lower()} y cómo haces tus tareas."]

    if inv:
        out += ["", "**Lo que encontré de tu rol** (con fuentes):"]
        out += [f"- {r}" for r in inv.get("obligaciones", [])[:4]]
        if inv.get("lineamientos"):
            out.append("Reglas que voy a seguir por eso:")
            out += [f"- {l['regla']}" for l in inv["lineamientos"][:5]]
        mias = revisar._palabras(" ".join(_tarea(t) for t in p.get("tareas", [])))
        otras = [t for t in inv.get("tareas_comunes", []) if len(revisar._palabras(t) & mias) < 2]
        if otras:
            out.append("Es habitual en tu rol hacer también esto; ¿lo haces?")
            out += [f"- {t}" for t in otras[:5]]

    atajos, de_skill = [], []
    for t in p.get("tareas", []):
        t = t if isinstance(t, dict) else {"tarea": str(t)}
        if t.get("skill"):
            de_skill.append(f"- {t['tarea']}: la hace tu habilidad **{t['skill']}**")
        else:
            atajos.append(f"- `/{comun.slug(t['tarea'], largo=40)}` — {t['tarea']}")
    if atajos or de_skill:
        out += ["", "**Tus tareas, a un comando de distancia:**"] + atajos + de_skill

    if resp.get("skills_existentes"):
        out += ["", "**Lo que ya tenías:**", revisar.resumen(resp)]

    progs = programas.lista(resp)
    faltan = [x["titulo"] for x in progs if not x["ok"]]
    if not faltan:
        out += ["", "**Programas:** ya tienes todo lo necesario."]
    else:
        uno = len(faltan) == 1
        out += ["", f"**Programas:** te falta{'' if uno else 'n'} {', '.join(faltan)}; "
                    f"te ofrezco instalarl{'o' if uno else 'os'} al final."]
    if resp.get("credenciales"):
        out.append("**Accesos que vamos a necesitar:** " + ", ".join(c.get("para", c["variable"])
                                                                    for c in resp["credenciales"])
                   + ". Te explico cómo guardarlos de forma segura cuando toque; nunca en el chat.")
    out += ["", "Nada se crea hasta que me digas que sí."]
    return "\n".join(out)


def main(argv=None) -> int:
    comun.utf8()
    ap = argparse.ArgumentParser(description="Propuesta del espacio en lenguaje sencillo")
    ap.add_argument("--raiz")
    ap.add_argument("--respuestas", default="respuestas-espacio.json")
    a = ap.parse_args(argv)
    raiz = comun.encontrar_raiz(a.raiz)
    p = Path(a.respuestas)
    p = p if p.is_absolute() else raiz / p
    try:
        resp = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        print("No hay respuestas-espacio.json: primero la entrevista.", file=sys.stderr)
        return 2
    print(propuesta(resp))
    return 0


if __name__ == "__main__":
    sys.exit(main())
