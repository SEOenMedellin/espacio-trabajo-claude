#!/usr/bin/env python3
"""Lista de arranque: lo que le falta a la persona para tener su espacio al
100 %, con su avance. El aviso de inicio la muestra mientras esté incompleta;
cuando la persona dice «sigamos», se completa lo siguiente.

    (sin argumentos)   avance y pendientes, con cómo completar cada uno
    --breve            una línea (la usa el aviso de inicio)
    --json

Código de salida: 0 completa, 1 hay pendientes, 2 sin espacio.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bitacora  # noqa: E402
import comun  # noqa: E402
import programas  # noqa: E402

IGNORAR = {".gitkeep", "README.md", "INDICE.md", ".DS_Store", "Thumbs.db", "desktop.ini"}


def _hay_archivos(carpeta: Path) -> bool:
    return carpeta.is_dir() and any(f.is_file() and f.name not in IGNORAR for f in carpeta.rglob("*"))


def pasos(raiz: Path, cfg: dict) -> list[dict]:
    res = [{"id": "espacio", "que": "Tu espacio de trabajo", "ok": True, "como": ""}]
    res.append({"id": "rol", "que": "Investigación de tu rol", "ok": bool(cfg.get("investigacion_rol")),
                "como": "Investigar el rol y sumar sus lineamientos (ampliar con primeros-pasos, paso 4)."})
    faltan = programas.faltantes(cfg)
    res.append({"id": "programas", "ok": not faltan,
                "que": "Programas para trabajar" + (f" (faltan: {', '.join(faltan)})" if faltan else ""),
                "como": "Instalar " + ", ".join(faltan) + " con programas.py --instalar <nombre>, uno por uno y "
                        "con el sí de la persona." if faltan else ""})
    if cfg.get("credenciales"):
        env = raiz / "credenciales" / ".env"
        texto = env.read_text(encoding="utf-8") if env.is_file() else ""
        vacias = [c["variable"] for c in cfg["credenciales"]
                  if not re.search(rf"^{re.escape(c['variable'])}=\S", texto, re.M)]
        res.append({"id": "accesos", "que": "Tus accesos guardados", "ok": not vacias,
                    "como": "Guiar a la persona para que escriba en credenciales/.env: " + ", ".join(vacias)
                            + " (nunca en el chat; ver credenciales.md)." if vacias else ""})
    unidades = comun.proyectos(cfg) or [None]
    contexto = any(_hay_archivos(raiz / comun.base_dir(comun.resolver(cfg, p)["contexto"])) for p in unidades)
    res.append({"id": "contexto", "que": "Documentos de tu proyecto", "ok": contexto,
                "como": "Pedirle los documentos del proyecto (briefs, manuales, normas, ejemplos) y llevarlos "
                        "a la carpeta de contexto."})
    sin_atajo = [a["tarea"] for a in comun.atajos(cfg) if not (raiz / a["ruta"]).is_file()]
    res.append({"id": "atajos", "que": "Atajos para tus tareas", "ok": not sin_atajo,
                "como": "Crear los atajos que faltan con montar.py (repara sin sobrescribir): "
                        + ", ".join(sin_atajo) if sin_atajo else ""})
    hecha = False
    for _, b in bitacora.todas(raiz, cfg):
        if b.is_file() and bitacora.parsear(b.read_text(encoding="utf-8"))[0]:
            hecha = True
            break
    res.append({"id": "primera", "que": "Tu primera tarea con Claude", "ok": hecha,
                "como": "Proponerle hacer juntos su tarea más frecuente con su atajo, y medir el tiempo ahorrado."})
    return res


def main(argv=None) -> int:
    comun.utf8()
    ap = argparse.ArgumentParser(description="Lista de arranque del espacio")
    ap.add_argument("--raiz")
    ap.add_argument("--breve", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    raiz = comun.encontrar_raiz(a.raiz)
    cfg = comun.leer_config(raiz)
    if cfg is None:
        print("Sin montar: no hay espacio.json.", file=sys.stderr)
        return 2
    ps = pasos(raiz, cfg)
    listos = sum(1 for p in ps if p["ok"])
    pendientes = [p for p in ps if not p["ok"]]
    if a.json:
        print(json.dumps({"listos": listos, "total": len(ps), "pasos": ps}, ensure_ascii=False, indent=2))
    elif a.breve:
        if pendientes:
            print(f"Arranque: {listos} de {len(ps)} listo. Falta: " + "; ".join(p["que"] for p in pendientes)
                  + ". Muéstraselo a la persona en una línea y, si dice «sigamos», completa el primero "
                  "(arranque.py dice cómo).")
    else:
        print(f"Arranque: {listos} de {len(ps)} listo")
        for p in ps:
            print(f"  {'✓' if p['ok'] else '·'} {p['que']}" + ("" if p["ok"] else f"\n      cómo: {p['como']}"))
    return 1 if pendientes else 0


if __name__ == "__main__":
    sys.exit(main())
