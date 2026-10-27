#!/usr/bin/env python3
"""Mide cuánto toma una tarea del rol con Claude, para compararlo con lo que
la persona tardaría a mano. Solo para tareas del trabajo de la persona
(informes, investigaciones, análisis…), nunca para configurar el espacio ni
crear skills.

    --empezar PROCESO     pone en marcha el reloj de la tarea (slug del proceso)
    --terminar            minutos desde --empezar (o, si no se llamó, desde el
                          inicio de la sesión) y detiene el reloj
    --estimacion PROCESO  última estimación manual de la persona para ese tipo
                          de tarea, para proponérsela en vez de preguntar de cero
    --proyecto P          en multiproyecto, el proyecto de la tarea
    --json

El resultado va a la entrada de la bitácora: `manual: <min> | claude: <min>`.
Código de salida: 0 bien, 1 no hay con qué medir o no hay estimación previa.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bitacora  # noqa: E402
import comun  # noqa: E402

LARGA = 8 * 60  # más de esto con el reloj corriendo: probablemente hubo pausas


def _estado(raiz: Path) -> Path:
    return raiz / comun.ESTADO / "tareas-en-curso.json"


def _leer(raiz: Path) -> dict:
    try:
        return json.loads(_estado(raiz).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _guardar(raiz: Path, datos: dict) -> None:
    comun.escribir(_estado(raiz), json.dumps(datos, ensure_ascii=False))


def inicio_sesion(raiz: Path) -> float | None:
    """El inicio de sesión más reciente de las últimas 12 horas."""
    carpeta = raiz / comun.ESTADO / "sesiones"
    ahora, mejor = time.time(), None
    for f in carpeta.glob("*.json") if carpeta.is_dir() else []:
        try:
            ini = float(json.loads(f.read_text(encoding="utf-8")).get("inicio", 0))
        except (OSError, ValueError, TypeError):
            continue
        if ahora - ini < 12 * 3600 and (mejor is None or ini > mejor):
            mejor = ini
    return mejor


def estimacion(raiz: Path, cfg: dict, proceso: str, proyecto: str | None) -> int | None:
    p = bitacora.ruta_bitacora(raiz, cfg, proyecto)
    if not p or not p.is_file():
        return None
    entradas, _ = bitacora.parsear(p.read_text(encoding="utf-8"))
    for e in reversed(entradas):
        if e.get("proceso") == proceso and e.get("manual"):
            return e["manual"]
    return None


def main(argv=None) -> int:
    comun.utf8()
    ap = argparse.ArgumentParser(description="Tiempo de una tarea con Claude")
    ap.add_argument("--raiz")
    ap.add_argument("--proyecto")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--empezar", metavar="PROCESO")
    g.add_argument("--terminar", action="store_true")
    g.add_argument("--estimacion", metavar="PROCESO")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    raiz = comun.encontrar_raiz(a.raiz)
    clave = a.proyecto or ""

    if a.empezar:
        datos = _leer(raiz)
        datos[clave] = {"proceso": a.empezar, "inicio": time.time()}
        _guardar(raiz, datos)
        print(f"Reloj en marcha para «{a.empezar}».")
        return 0

    if a.estimacion:
        cfg = comun.leer_config(raiz) or {}
        m = estimacion(raiz, cfg, a.estimacion, a.proyecto)
        if a.json:
            print(json.dumps({"proceso": a.estimacion, "manual": m}))
        elif m:
            print(f"La última vez la persona estimó {comun.duracion(m)} a mano ({m} min).")
        else:
            print("Sin estimación previa para este tipo de tarea: pregúntala.")
        return 0 if m else 1

    datos = _leer(raiz)
    tarea = datos.pop(clave, None)
    if tarea:
        _guardar(raiz, datos)
        desde, inicio = "tarea", tarea["inicio"]
    else:
        desde, inicio = "sesion", inicio_sesion(raiz)
    if inicio is None:
        if a.json:
            print(json.dumps({"minutos": None, "desde": None}))
        else:
            print("No hay reloj para esta tarea: estima con la persona cuánto tiempo le dedicaron con Claude.")
        return 1
    minutos = max(1, math.ceil((time.time() - inicio) / 60))
    if a.json:
        print(json.dumps({"minutos": minutos, "desde": desde, "proceso": (tarea or {}).get("proceso"),
                          "revisar": minutos > LARGA}))
    else:
        print(f"Con Claude: {comun.duracion(minutos)} ({minutos} min, medido desde "
              f"{'el inicio de la tarea' if desde == 'tarea' else 'el inicio de la sesión'}).")
        if minutos > LARGA:
            print("Es mucho tiempo con el reloj corriendo: pregúntale a la persona cuánto fue de trabajo real.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
