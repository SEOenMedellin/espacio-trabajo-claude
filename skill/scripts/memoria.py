#!/usr/bin/env python3
"""Valida la memoria de trabajo y regenera el INDICE.md de cada ámbito.

Un nodo es un archivo `<id>.md` con este encabezado:

    ---
    id: <id, igual al nombre del archivo>
    titulo: <una línea>
    tipo: restriccion | solucion | decision | proceso | dato | preferencia
    ambito: global | <proyecto>
    fecha: DD-mmm-YYYY
    tags: [a, b]
    relacionado: [otro-id]
    ---

Ámbitos: la memoria global (rol `memoria_global`) es conocimiento que sirve a
cualquier proyecto; en modo multiproyecto, cada proyecto tiene la suya (rol
`memoria_proyecto`). Un nodo de proyecto puede enlazar a uno global; uno global
nunca enlaza a uno de proyecto (deja de ser agnóstico): eso es un error.

El índice es derivado: si diverge del disco, gana el disco.

Uso (desde la raíz):
    python <skill>/scripts/memoria.py             estado y errores
    python <skill>/scripts/memoria.py --rebuild   regenera cada INDICE.md
    python <skill>/scripts/memoria.py --json

Código de salida: 0 bien, 1 hay errores, 2 no hay espacio.json.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun  # noqa: E402

EXCLUIDOS = {"README.md", "INDICE.md"}
ENLACE = re.compile(r"\[\[([a-z0-9\-]+)\]\]")
OBLIGATORIOS = ("id", "titulo", "tipo", "ambito", "fecha")


def leer_nodo(p: Path) -> dict:
    texto = p.read_text(encoding="utf-8", errors="replace")
    meta: dict = {"archivo": p, "cuerpo": texto}
    if texto.startswith("---"):
        partes = texto.split("---", 2)
        if len(partes) == 3:
            for linea in partes[1].splitlines():
                if ":" in linea:
                    k, v = linea.split(":", 1)
                    v = v.strip()
                    if v.startswith("[") and v.endswith("]"):
                        v = [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
                    else:
                        v = v.strip("'\"")
                    meta[k.strip()] = v
            meta["cuerpo"] = partes[2]
    # relacionado: [id, requiere:id, resuelve:id, deriva_en:id] — sin tipo es «relacionado»
    relaciones = {("relacionado", e) for e in ENLACE.findall(meta["cuerpo"])}
    rel = meta.get("relacionado") or []
    for x in (rel if isinstance(rel, list) else [rel]):
        tipo, _, ident = x.partition(":") if ":" in x else ("relacionado", "", x)
        if ident:
            relaciones.add((tipo.strip() if tipo.strip() in comun.RELACIONES else "relacionado", ident.strip()))
    meta["relaciones"] = sorted(relaciones)
    meta["enlaces"] = sorted({e for _, e in relaciones if e})
    return meta


def ambitos(raiz: Path, cfg: dict) -> dict[str, Path]:
    """{'global': memoria/, '<proyecto>': proyectos/<p>/memoria/, ...}"""
    res = {}
    glob = cfg.get("rutas", {}).get("memoria_global")
    if glob:
        res["global"] = raiz / comun.base_dir(glob)
    for p in comun.proyectos(cfg):
        r = comun.resolver(cfg, p).get("memoria_proyecto")
        if r:
            res[p] = raiz / comun.base_dir(r)
    return res


def nodos(raiz: Path, cfg: dict) -> tuple[list[dict], list[str]]:
    todos, errores = [], []
    for ambito, carpeta in ambitos(raiz, cfg).items():
        if not carpeta.is_dir():
            continue
        for f in sorted(carpeta.glob("*.md")):
            if f.name in EXCLUIDOS:
                continue
            n = leer_nodo(f)
            n["ambito_carpeta"] = ambito
            faltan = [c for c in OBLIGATORIOS if not n.get(c)]
            if faltan:
                errores.append(f"{f.name}: faltan campos {', '.join(faltan)}")
            if n.get("id") and n["id"] != f.stem:
                errores.append(f"{f.name}: el id '{n['id']}' no coincide con el nombre del archivo")
            if n.get("tipo") and n["tipo"] not in comun.TIPOS_MEMORIA:
                errores.append(f"{f.name}: tipo '{n['tipo']}' no es {'|'.join(comun.TIPOS_MEMORIA)}")
            todos.append(n)
    por_id = {n.get("id") or n["archivo"].stem: n for n in todos}
    for n in todos:
        for e in n["enlaces"]:
            destino = por_id.get(e)
            if destino is None:
                errores.append(f"{n['archivo'].name}: enlaza a '{e}', que no existe")
            elif n["ambito_carpeta"] == "global" and destino["ambito_carpeta"] != "global":
                errores.append(f"{n['archivo'].name}: un nodo global no puede enlazar al proyecto ('{e}')")
    return todos, errores


def indice(ambito: str, lista: list[dict]) -> str:
    filas = [f"# Índice de memoria — {ambito}", "",
             "Generado por `memoria.py --rebuild`. No se edita a mano: si diverge del disco, gana el disco.",
             "Se lee este índice para decidir qué nodo abrir; luego se abre solo ese nodo.", "",
             "| id | tipo | título | tags | enlaces |", "|---|---|---|---|---|"]
    for n in sorted(lista, key=lambda x: (x.get("tipo", ""), x.get("id", ""))):
        tags = n.get("tags") or []
        tags = ", ".join(tags) if isinstance(tags, list) else tags
        filas.append(f"| [{n.get('id', n['archivo'].stem)}]({n['archivo'].name}) | {n.get('tipo', '')} | "
                     f"{n.get('titulo', '')} | {tags} | {', '.join(n['enlaces'])} |")
    if len(lista) == 0:
        filas.append("| — | — | Todavía no hay nodos | — | — |")
    return "\n".join(filas) + "\n"


def rebuild(raiz: Path, cfg: dict) -> list[str]:
    todos, _ = nodos(raiz, cfg)
    hechos = []
    for ambito, carpeta in ambitos(raiz, cfg).items():
        if not carpeta.is_dir():
            continue
        lista = [n for n in todos if n["ambito_carpeta"] == ambito]
        comun.escribir(carpeta / "INDICE.md", indice(ambito, lista))
        hechos.append(f"{ambito}: INDICE.md con {len(lista)} nodo(s)")
    return hechos


def main(argv=None) -> int:
    comun.utf8()
    ap = argparse.ArgumentParser(description="Memoria de trabajo: validar y regenerar índices")
    ap.add_argument("--raiz")
    ap.add_argument("--rebuild", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    raiz = comun.encontrar_raiz(a.raiz)
    cfg = comun.leer_config(raiz)
    if cfg is None:
        print("No hay espacio.json: el espacio no está montado (usa primeros-pasos).", file=sys.stderr)
        return 2
    if a.rebuild:
        for h in rebuild(raiz, cfg):
            print(h)
    todos, errores = nodos(raiz, cfg)
    if a.json:
        print(json.dumps({"nodos": [{k: v for k, v in n.items() if k not in ("archivo", "cuerpo")}
                                    | {"archivo": n["archivo"].relative_to(raiz).as_posix()} for n in todos],
                          "errores": errores}, ensure_ascii=False, indent=2))
    elif not a.rebuild:
        print(f"{len(todos)} nodo(s) de memoria")
    for e in errores:
        print(f"ERROR: {e}", file=sys.stderr)
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
