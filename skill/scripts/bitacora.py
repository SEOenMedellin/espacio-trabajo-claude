#!/usr/bin/env python3
"""Lee, valida y mantiene la bitácora de peticiones (rol `bitacora_peticiones`).

Formato exacto de una entrada (lo parsean este script y grafo.py):

    ### P-NNN — <título>
    <!-- fecha: DD-mmm-YYYY | skills: a, b | memoria: id1 | archivos: ruta1 | proceso: <slug> | estado: resuelta|parcial|abierta -->

    **Petición:** ...
    **Cómo se resolvió:** ...
    **Patrones y atajos:** ...          (opcional)
    **Conocimiento adyacente:** ...     (opcional)
    **Corrección del usuario:** ...     (opcional)

La tabla "Procesos candidatos" del final se genera agrupando por `proceso`,
entre <!-- procesos-candidatos:inicio --> y <!-- procesos-candidatos:fin -->.
La columna "Decisión" es lo único manual y se conserva al regenerar.

Uso (desde la raíz):
    python <skill>/scripts/bitacora.py [--proyecto P]               resumen + validación
    python <skill>/scripts/bitacora.py [--proyecto P] --siguiente   próximo P-NNN
    python <skill>/scripts/bitacora.py [--proyecto P] --tabla       regenera "Procesos candidatos"
    python <skill>/scripts/bitacora.py [--proyecto P] --json

Código de salida: 0 bien, 1 entradas mal formadas, 2 no existe la bitácora.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun  # noqa: E402

TITULO = re.compile(r"^### (P-\d{3,}) — (.+?)\s*$")
META = re.compile(r"^<!--\s*(.*?)\s*-->\s*$")
CAMPOS = ("fecha", "skills", "memoria", "archivos", "proceso", "estado")
LISTAS = ("skills", "memoria", "archivos")
ESTADOS = ("resuelta", "parcial", "abierta")
INICIO = "<!-- procesos-candidatos:inicio -->"
FIN = "<!-- procesos-candidatos:fin -->"
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FECHA = re.compile(r"^\d{2}-(" + "|".join(comun.MESES) + r")-\d{4}$")


def parsear(texto: str) -> tuple[list[dict], list[str]]:
    lineas = texto.splitlines()
    entradas, errores = [], []
    for i, l in enumerate(lineas):
        m = TITULO.match(l)
        if not m:
            if l.startswith("### P-"):
                errores.append(f"línea {i + 1}: título mal formado (usa '### P-NNN — título')")
            continue
        e = {"id": m.group(1), "titulo": m.group(2), "linea": i + 1}
        j = i + 1
        while j < len(lineas) and not lineas[j].strip():
            j += 1
        meta = META.match(lineas[j]) if j < len(lineas) else None
        if not meta:
            errores.append(f"{e['id']}: falta la línea de metadatos debajo del título")
            entradas.append(e)
            continue
        for parte in meta.group(1).split("|"):
            if ":" in parte:
                k, v = (x.strip() for x in parte.split(":", 1))
                e[k] = [x.strip() for x in v.split(",") if x.strip()] if k in LISTAS else v
        faltan = [c for c in CAMPOS if c not in e]
        if faltan:
            errores.append(f"{e['id']}: faltan campos en metadatos: {', '.join(faltan)}")
        if e.get("fecha") and not FECHA.match(e["fecha"]):
            errores.append(f"{e['id']}: la fecha {e['fecha']!r} no es DD-mmm-YYYY")
        if e.get("estado") and e["estado"] not in ESTADOS:
            errores.append(f"{e['id']}: estado {e['estado']!r} no es {'|'.join(ESTADOS)}")
        if e.get("proceso") and not SLUG.match(e["proceso"]):
            errores.append(f"{e['id']}: proceso {e['proceso']!r} no es un slug kebab-case")
        cuerpo = []
        for l2 in lineas[j + 1:]:
            if l2.startswith("### ") or l2.startswith("## ") or l2.strip() == INICIO:
                break
            cuerpo.append(l2)
        t = "\n".join(cuerpo)
        e["texto"] = t.strip()
        e["correccion"] = "**Corrección del usuario:**" in t
        if "**Petición:**" not in t or "**Cómo se resolvió:**" not in t:
            errores.append(f"{e['id']}: faltan **Petición:** o **Cómo se resolvió:**")
        entradas.append(e)
    ids = [e["id"] for e in entradas]
    for d in sorted({x for x in ids if ids.count(x) > 1}):
        errores.append(f"{d}: id repetido")
    return entradas, errores


def siguiente(entradas: list[dict]) -> str:
    n = max((int(e["id"][2:]) for e in entradas), default=0)
    return f"P-{n + 1:03d}"


def decisiones_previas(texto: str) -> dict:
    if INICIO not in texto:
        return {}
    res = {}
    for l in texto.split(INICIO, 1)[1].split(FIN, 1)[0].splitlines():
        celdas = [c.strip() for c in l.strip().strip("|").split("|")]
        if len(celdas) >= 6 and celdas[0].startswith("`"):
            res[celdas[0].strip("`")] = celdas[5]
    return res


def tabla(entradas: list[dict], decisiones: dict) -> str:
    grupos: dict[str, list[dict]] = {}
    for e in entradas:
        if e.get("proceso"):
            grupos.setdefault(e["proceso"], []).append(e)
    filas = ["| Proceso | Peticiones | Veces | Correcciones | Candidato a skill | Decisión |",
             "|---|---|---|---|---|---|"]
    for slug, es in sorted(grupos.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        corr = sum(1 for e in es if e.get("correccion"))
        cand = "sí" if len(es) >= 2 or corr else "no"
        filas.append(f"| `{slug}` | {', '.join(e['id'] for e in es)} | {len(es)} | {corr} | {cand} | "
                     f"{decisiones.get(slug, 'pendiente' if cand == 'sí' else '—')} |")
    if len(filas) == 2:
        filas.append("| — | — | 0 | 0 | — | — |")
    return "\n".join(filas)


def regenerar(p: Path) -> bool:
    texto = p.read_text(encoding="utf-8")
    entradas, _ = parsear(texto)
    nueva = INICIO + "\n" + tabla(entradas, decisiones_previas(texto)) + "\n" + FIN
    if INICIO in texto and FIN in texto:
        resultado = texto.split(INICIO, 1)[0] + nueva + texto.split(FIN, 1)[1]
    else:
        resultado = texto.rstrip("\n") + "\n\n## Procesos candidatos\n\n" + nueva + "\n"
    if resultado != texto:
        comun.escribir(p, resultado)
        return True
    return False


def ruta_bitacora(raiz: Path, cfg: dict, proyecto: str | None) -> Path | None:
    r = comun.resolver(cfg, proyecto).get("bitacora_peticiones")
    if not r or "<proyecto>" in r:
        return None
    return raiz / r


def todas(raiz: Path, cfg: dict) -> list[tuple[str, Path]]:
    """[(proyecto o '', ruta)] de cada bitácora de peticiones del espacio."""
    lista = comun.proyectos(cfg)
    if not lista:
        p = ruta_bitacora(raiz, cfg, None)
        return [("", p)] if p else []
    return [(x, ruta_bitacora(raiz, cfg, x)) for x in lista if ruta_bitacora(raiz, cfg, x)]


def main(argv=None) -> int:
    comun.utf8()
    ap = argparse.ArgumentParser(description="Bitácora de peticiones")
    ap.add_argument("--raiz")
    ap.add_argument("--proyecto")
    ap.add_argument("--siguiente", action="store_true")
    ap.add_argument("--tabla", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    raiz = comun.encontrar_raiz(a.raiz)
    cfg = comun.leer_config(raiz)
    if cfg is None:
        print("No hay espacio.json: el espacio no está montado (usa primeros-pasos).", file=sys.stderr)
        return 2
    p = ruta_bitacora(raiz, cfg, a.proyecto)
    if p is None:
        print("Hay varios proyectos: indica cuál con --proyecto "
              f"({', '.join(comun.proyectos(cfg))}).", file=sys.stderr)
        return 2
    if not p.is_file():
        print(f"No existe {p.relative_to(raiz).as_posix()}. Repara el espacio con primeros-pasos.", file=sys.stderr)
        return 2
    entradas, errores = parsear(p.read_text(encoding="utf-8"))
    if a.siguiente:
        print(siguiente(entradas))
        return 0
    if a.tabla:
        cambio = regenerar(p)
        print(f"Procesos candidatos {'regenerada' if cambio else 'sin cambios'}")
    if a.json:
        print(json.dumps({"entradas": entradas, "errores": errores}, ensure_ascii=False, indent=2))
    elif not a.tabla:
        print(f"{len(entradas)} peticiones · próxima: {siguiente(entradas)}")
    for err in errores:
        print(f"ERROR: {err}", file=sys.stderr)
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
