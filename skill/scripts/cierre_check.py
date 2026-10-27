#!/usr/bin/env python3
"""Hook Stop: recuerda el protocolo de cierre una sola vez por sesión.

Bloquea el fin del turno (una vez) solo si, desde que empezó la sesión,
cambiaron archivos en las carpetas de trabajo y ninguna bitácora de peticiones
se tocó. El motivo del bloqueo le pide a Claude correr el protocolo de cierre
(docs/espacio-de-trabajo/bitacoras.md).

Nunca entra en bucle: respeta stop_hook_active, avisa una sola vez por sesión
y, si no hay marca de inicio (el hook SessionStart no corrió), la crea y no
bloquea. Cualquier error se traga: un recordatorio nunca rompe la sesión.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bitacora  # noqa: E402
import comun  # noqa: E402

IGNORAR = {"INDICE.md", ".gitkeep"}


def carpetas_trabajo(raiz: Path, cfg: dict) -> list[Path]:
    res = []
    lista = comun.proyectos(cfg)
    if lista:
        base = cfg.get("proyectos", {}).get("base", "proyectos")
        res += [raiz / base / p for p in lista]
    for rol in ("contexto", "entregables", "investigacion", "memoria_global"):
        r = cfg.get("rutas", {}).get(rol)
        if r and "<proyecto>" not in r:
            res.append(raiz / comun.base_dir(r))
    for c in cfg.get("arquitectura", {}).get("carpetas", []):
        if "<proyecto>" not in c.get("ruta", ""):
            res.append(raiz / comun.base_dir(c["ruta"]))
    return [c for c in res if c != raiz]


def cambios(carpetas: list[Path], inicio: float, excluir: set[Path], raiz: Path) -> list[str]:
    res = []
    for carpeta in carpetas:
        if not carpeta.is_dir():
            continue
        for f in carpeta.rglob("*"):
            if not f.is_file() or f.name in IGNORAR or f in excluir or "__pycache__" in f.parts:
                continue
            try:
                if f.stat().st_mtime > inicio:
                    res.append(f.relative_to(raiz).as_posix())
            except OSError:
                continue
            if len(res) >= 10:
                return res
    return res


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0
    if not isinstance(payload, dict) or payload.get("stop_hook_active"):
        return 0
    raiz = comun.encontrar_raiz()
    cfg = comun.leer_config(raiz)
    if cfg is None:
        return 0
    sid = payload.get("session_id") or ""
    estado = comun.sesion_leer(raiz, sid)
    if not estado:
        comun.sesion_guardar(raiz, sid, {"inicio": time.time(), "avisado": False})
        return 0
    if estado.get("avisado"):
        return 0
    inicio = float(estado.get("inicio") or time.time())
    bitacoras = {p for _, p in bitacora.todas(raiz, cfg)}
    for b in bitacoras:
        try:
            if b.is_file() and b.stat().st_mtime > inicio:
                return 0
        except OSError:
            continue
    movidos = set()
    log = raiz / comun.ESTADO / "movimientos.log"
    if log.is_file():
        for l in log.read_text(encoding="utf-8").splitlines():
            partes = l.split("\t")
            if len(partes) == 3:
                movidos.add(partes[2])
    hechos = [h for h in cambios(carpetas_trabajo(raiz, cfg), inicio, bitacoras, raiz)
              if h not in movidos and not h.endswith("/README.md")]
    if not hechos:
        return 0
    estado["avisado"] = True
    comun.sesion_guardar(raiz, sid, estado)
    muestra = ", ".join(hechos[:5]) + ("…" if len(hechos) > 5 else "")
    print(json.dumps({
        "decision": "block",
        "reason": (
            f"Cambiaron archivos de trabajo ({muestra}) y la bitácora de peticiones no se actualizó. "
            "Si la tarea terminó, corre el protocolo de cierre (docs/espacio-de-trabajo/bitacoras.md): "
            "di en una frase qué se hizo y qué vas a recordar, y pregunta con una AskUserQuestion "
            "'¿Lo guardo así para la próxima vez?' (Sí, guárdalo / Corrige algo / No hace falta). "
            "Después: entrada P-NNN, nodo de memoria si se aprendió algo, bitacora.py --tabla y "
            "grafo.py --actualizar. Solo se registra trabajo del rol de la persona: si lo que cambió "
            "fue configuración del espacio, carpetas, credenciales, skills o ajustes del sistema, no se "
            "registra nada. Si la tarea sigue abierta, termina el turno sin mencionarlo: "
            "este recordatorio no se repite en la sesión."
        ),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    comun.utf8()
    try:
        sys.exit(main())
    except Exception:  # noqa: BLE001
        sys.exit(0)
