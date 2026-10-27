#!/usr/bin/env python3
"""Abre y cierra cada tarea del trabajo de la persona (un informe, una
investigación, un análisis; nunca configurar el espacio ni crear skills), para
que Claude no gaste tiempo ni tokens en el papeleo.

    --empezar --proceso P --categoria C [--titulo T] [--proyecto X]
        da el id (P-NNN), crea la carpeta <categoria>/<P-NNN>-<fecha>/ en los
        entregables y pone el reloj en marcha.

    --cerrar --datos cierre.json [--proyecto X]      (o --datos - para leer de stdin)
        con lo que Claude escribe en cierre.json (titulo, peticion, como y, si
        los hay, patrones, adyacente, correccion, skills, memoria, deriva_en,
        estado, manual en minutos), escribe la entrada de la bitácora con fecha
        y hora, deja memoria.md junto al entregable, calcula el tiempo
        ahorrado y actualiza la tabla de procesos, la memoria y el grafo.

Código de salida: 0 bien, 1 algo falló (dice qué), 2 datos incompletos.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bitacora  # noqa: E402
import comun  # noqa: E402
import grafo  # noqa: E402
import memoria  # noqa: E402
import tiempo  # noqa: E402


def empezar(raiz: Path, cfg: dict, proceso: str, categoria: str, titulo: str, proyecto: str | None) -> dict:
    p = bitacora.ruta_bitacora(raiz, cfg, proyecto)
    if p is None or not p.is_file():
        raise SystemExit("No encuentro la bitácora" + (" (indica --proyecto)" if comun.proyectos(cfg) else "")
                         + ": repara el espacio con primeros-pasos.")
    estado = tiempo._leer(raiz)
    reservados = {t.get("id") for t in estado.values() if t.get("bitacora") == str(p)}
    entradas, _ = bitacora.parsear(p.read_text(encoding="utf-8"))
    id_ = bitacora.siguiente(entradas)
    while id_ in reservados:
        id_ = f"P-{int(id_[2:]) + 1:03d}"
    fecha = comun.hoy()
    carpeta = comun.carpeta_tarea(cfg, proyecto, comun.slug(categoria, largo=30), id_, fecha)
    (raiz / carpeta).mkdir(parents=True, exist_ok=True)
    clave = proyecto or ""
    estado[clave] = {"proceso": comun.slug(proceso, largo=40), "inicio": time.time(), "id": id_, "carpeta": carpeta,
                     "titulo": titulo, "fecha": fecha, "bitacora": str(p)}
    tiempo._guardar(raiz, estado)
    return estado[clave]


def memoria_md(t: dict, d: dict, entrada: dict) -> str:
    out = [f"# {entrada['id']} — {entrada['titulo']}", "",
           f"- **Fecha:** {entrada['fecha']} a las {entrada['hora']}",
           f"- **Tipo de tarea:** `{entrada.get('proceso', '')}`", f"- **Estado:** {entrada['estado']}"]
    if entrada.get("manual") and entrada.get("claude"):
        out.append(f"- **Tiempo:** {comun.duracion(entrada['claude'])} con Claude frente a "
                   f"{comun.duracion(entrada['manual'])} a mano (ahorro: "
                   f"{comun.duracion(entrada['manual'] - entrada['claude'])})")
    out += ["", "## Qué se pidió", "", entrada["peticion"], "", "## Cómo se resolvió", "", entrada["como"], ""]
    for clave, titulo in (("patrones", "Patrones y atajos"), ("adyacente", "Conocimiento adyacente"),
                          ("correccion", "Corrección de la persona")):
        if d.get(clave):
            out += [f"## {titulo}", "", d[clave], ""]
    rel = [("requiere", f"skill `{s}`") for s in d.get("skills", [])]
    rel += [("requiere", f"memoria `{m}`") for m in d.get("memoria", [])]
    rel += [("resuelve", f"proceso `{entrada['proceso']}`")] if entrada.get("proceso") else []
    rel += [("deriva_en", f"`{a}`") for a in entrada.get("archivos", [])]
    rel += [("deriva_en", f"`{x}`") for x in d.get("deriva_en", [])]
    if rel:
        out += ["## Relaciones", ""] + [f"- {r} → {x}" for r, x in rel] + [""]
    return "\n".join(out)


def cerrar(raiz: Path, cfg: dict, d: dict, proyecto: str | None) -> tuple[dict, str]:
    faltan = [k for k in ("titulo", "peticion", "como") if not str(d.get(k, "")).strip()]
    if faltan:
        raise ValueError("faltan en los datos del cierre: " + ", ".join(faltan))
    estado = tiempo._leer(raiz)
    t = estado.pop(proyecto or "", None) or {}
    p = Path(t["bitacora"]) if t.get("bitacora") else bitacora.ruta_bitacora(raiz, cfg, proyecto)
    if p is None or not p.is_file():
        raise ValueError("no encuentro la bitácora: repara el espacio con primeros-pasos")
    entradas, _ = bitacora.parsear(p.read_text(encoding="utf-8"))
    id_ = t.get("id") or bitacora.siguiente(entradas)
    if any(e["id"] == id_ for e in entradas):
        id_ = bitacora.siguiente(entradas)
    inicio = t.get("inicio") or tiempo.inicio_sesion(raiz)
    claude = d.get("claude") or (max(1, math.ceil((time.time() - inicio) / 60)) if inicio else None)
    carpeta = t.get("carpeta")
    archivos = d.get("archivos")
    if archivos is None and carpeta and (raiz / carpeta).is_dir():
        archivos = sorted(f.relative_to(raiz).as_posix() for f in (raiz / carpeta).rglob("*")
                          if f.is_file() and f.name != "memoria.md")
    ahora = dt.datetime.now()
    entrada = {"id": id_, "titulo": d["titulo"].strip(), "fecha": t.get("fecha") or comun.hoy(),
               "hora": ahora.strftime("%H:%M"), "skills": d.get("skills", []), "memoria": d.get("memoria", []),
               "archivos": archivos or [], "proceso": comun.slug(d.get("proceso") or t.get("proceso") or "", largo=40)
               if (d.get("proceso") or t.get("proceso")) else "", "estado": d.get("estado", "resuelta"),
               "deriva_en": d.get("deriva_en", []), "peticion": d["peticion"].strip(), "como": d["como"].strip(),
               "patrones": d.get("patrones"), "adyacente": d.get("adyacente"), "correccion": d.get("correccion"),
               "manual": int(d["manual"]) if d.get("manual") else None, "claude": int(claude) if claude else None}
    if entrada["estado"] not in bitacora.ESTADOS:
        raise ValueError(f"estado debe ser {' | '.join(bitacora.ESTADOS)}")
    bitacora.insertar(p, bitacora.formatear(entrada))
    _, errores = bitacora.parsear(p.read_text(encoding="utf-8"))
    if any(e.startswith(id_) for e in errores):
        raise ValueError("la entrada quedó mal formada: " + "; ".join(e for e in errores if e.startswith(id_)))
    if carpeta:
        comun.escribir(raiz / carpeta / "memoria.md", memoria_md(t, d, entrada))
    tiempo._guardar(raiz, estado)
    bitacora.regenerar(p)
    memoria.rebuild(raiz, cfg)
    grafo.actualizar(raiz, cfg)
    frase = f"Tarea {id_} registrada."
    if entrada["manual"] and entrada["claude"]:
        frase = (f"Con Claude: {comun.duracion(entrada['claude'])}; a mano: {comun.duracion(entrada['manual'])}. "
                 + (f"Te ahorraste {comun.duracion(entrada['manual'] - entrada['claude'])}."
                    if entrada["manual"] > entrada["claude"] else "Esta vez no hubo ahorro de tiempo."))
    return entrada, frase


def main(argv=None) -> int:
    comun.utf8()
    ap = argparse.ArgumentParser(description="Abrir y cerrar una tarea del rol")
    ap.add_argument("--raiz")
    ap.add_argument("--proyecto")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--empezar", action="store_true")
    g.add_argument("--cerrar", action="store_true")
    ap.add_argument("--proceso")
    ap.add_argument("--categoria")
    ap.add_argument("--titulo", default="")
    ap.add_argument("--datos")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    raiz = comun.encontrar_raiz(a.raiz)
    cfg = comun.leer_config(raiz)
    if cfg is None:
        print("El espacio no está montado: usa primeros-pasos.", file=sys.stderr)
        return 2
    if a.empezar:
        if not a.proceso or not a.categoria:
            print("--empezar necesita --proceso y --categoria", file=sys.stderr)
            return 2
        t = empezar(raiz, cfg, a.proceso, a.categoria, a.titulo, a.proyecto)
        print(json.dumps(t, ensure_ascii=False) if a.json else
              f"Tarea {t['id']} en marcha. Guarda el entregable en {t['carpeta']}/")
        return 0
    if not a.datos:
        print("--cerrar necesita --datos cierre.json (o - para stdin)", file=sys.stderr)
        return 2
    try:
        texto = sys.stdin.read() if a.datos == "-" else (raiz / a.datos if not Path(a.datos).is_absolute()
                                                         else Path(a.datos)).read_text(encoding="utf-8")
        datos = json.loads(texto)
        entrada, frase = cerrar(raiz, cfg, datos, a.proyecto)
    except (OSError, ValueError) as e:
        print(f"No se pudo cerrar la tarea: {e}", file=sys.stderr)
        return 2
    if a.datos != "-" and Path(a.datos).name == "cierre.json":
        (raiz / a.datos if not Path(a.datos).is_absolute() else Path(a.datos)).unlink(missing_ok=True)
    print(json.dumps({"id": entrada["id"], "frase": frase}, ensure_ascii=False) if a.json else frase)
    return 0


if __name__ == "__main__":
    sys.exit(main())
