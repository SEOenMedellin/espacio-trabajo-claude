#!/usr/bin/env python3
"""Arma solo el borrador de la revisión de los skills que ya traía el
repositorio, para que Claude no gaste tiempo ni tokens en lo mecánico:

- qué hace cada skill y qué tareas de la persona cubre,
- las reglas que impone,
- los problemas y contradicciones que encontró auditar.py (con decisión
  «pendiente»),
- los datos que conviene validar (normas, versiones, cifras, enlaces), como
  «no verificado».

Lo deja en respuestas-espacio.json → skills_existentes (sin borrar lo que
Claude ya haya validado o decidido) y marca en perfil.tareas qué tarea cubre
cada skill. A Claude le queda solo: validar los datos de --pendientes, revisar
los hallazgos y decidir con la persona.

    --borrador        crea o completa el bloque y muestra el resumen en sencillo
    --pendientes      datos por validar (lo único que requiere buscar)
    --resumen         el resumen en sencillo, para mostrárselo a la persona
    --respuestas R    otro archivo de respuestas (por defecto respuestas-espacio.json)

Código de salida: 0 bien, 2 sin respuestas que completar (haz antes la entrevista).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import auditar  # noqa: E402
import comun  # noqa: E402
import inventario  # noqa: E402

DATO = re.compile(r"(?i)https?://|\bv?\d+\.\d+(\.\d+)?\b|\b(norma|ley|decreto|resoluci[oó]n|art[ií]culo|iso|"
                  r"est[aá]ndar|standard|regulaci[oó]n|precio|tarifa|costo|l[ií]mite|m[aá]ximo|m[ií]nimo)\b|"
                  r"\d+\s?(%|px|ms|mb|gb|kb|caracteres|d[ií]as|horas)")
URL = re.compile(r"https?://[^\s)>\]\"'`]+")
MAX_DATOS = 8


def _palabras(texto: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]{4,}", comun.sin_acentos(texto.lower())) if w not in auditar.VACIAS}


def datos(raiz: Path, s: dict) -> list[dict]:
    res, vistos = [], set()
    for a in s["archivos"]:
        if not a.endswith(".md"):
            continue
        texto = auditar._leer(raiz / s["ruta"] / a)
        texto = texto.split("---", 2)[2] if texto.startswith("---") and texto.count("---") >= 2 else texto
        for linea in texto.splitlines():
            l = " ".join(linea.strip(" -*#>|").split())
            if 20 <= len(l) <= 220 and DATO.search(l) and l not in vistos and not l.startswith(("```", "python ")):
                vistos.add(l)
                d = {"dato": l[:180], "estado": "no verificado"}
                u = URL.search(l)
                if u:
                    d["fuente_en_skill"] = u.group(0).rstrip(".,;")
                res.append(d)
                if len(res) >= MAX_DATOS:
                    return res
    return res


def tareas_cubiertas(s: dict, tareas: list) -> list[str]:
    clave = _palabras(s["nombre"].replace("-", " ") + " " + s["descripcion"])
    nombre = _palabras(s["nombre"].replace("-", " "))
    res = []
    for t in tareas:
        texto = t.get("tarea", "") if isinstance(t, dict) else str(t)
        p = _palabras(texto)
        if (nombre and nombre <= p) or len(p & clave) >= 2:
            res.append(texto)
    return res


def borrador(raiz: Path, resp: dict) -> dict:
    inv = inventario.inventario(raiz)
    hall = auditar.auditar(raiz)
    reglas = auditar.reglas(raiz, inv)
    previo = {s["nombre"].lower(): s for s in (resp.get("skills_existentes") or {}).get("skills", [])}
    tareas = resp.get("perfil", {}).get("tareas", [])
    skills = []
    for s in inv["skills"]:
        ya = previo.get(s["nombre"].lower(), {})
        fuente = next((k for k in reglas if k == s["nombre"] or k.endswith(f"({s['ruta']})")), s["nombre"])
        problemas = [{"gravedad": h["gravedad"], "tipo": h["tipo"], "que": h["que"], "donde": h["donde"],
                      "sugerencia": h["sugerencia"], "sencillo": h["sencillo"], "decision": "pendiente"}
                     for h in hall if s["ruta"] in h["donde"] or h["donde"].startswith(s["nombre"] + ":")
                     or h["que"].startswith(s["nombre"] + ":")]
        decididos = {p["que"]: p for p in ya.get("problemas", [])}
        validados = {d["dato"]: d for d in ya.get("conocimiento", [])}
        skills.append({
            "nombre": s["nombre"], "ruta": s["ruta"],
            "para": ya.get("para") or s["descripcion"][:200].rstrip(". ") or "Sin descripción: completar",
            "tareas": ya.get("tareas") or tareas_cubiertas(s, tareas),
            "reglas": ya.get("reglas") or reglas.get(fuente, [])[:8],
            "conocimiento": [validados.get(d["dato"], d) for d in datos(raiz, s)]
                            + [d for k, d in validados.items() if k not in {x["dato"] for x in datos(raiz, s)}],
            "problemas": [decididos.get(p["que"], p) for p in problemas],
        })
    contradicciones = (resp.get("skills_existentes") or {}).get("contradicciones") or [
        {"entre": [x.strip() for x in re.split(r",| / ", h["donde"]) if x.strip()][:4] or ["?", "?"],
         "que": h["que"], "decision": "pendiente"}
        for h in hall if h["tipo"] == "contradiccion" and ("," in h["donde"] or " / " in h["donde"])]
    for c in contradicciones:
        if len(c["entre"]) < 2:
            c["entre"].append("espacio")
    bloque = {"fecha": (resp.get("skills_existentes") or {}).get("fecha") or comun.hoy(), "skills": skills,
              "contradicciones": contradicciones,
              "fuentes": (resp.get("skills_existentes") or {}).get("fuentes", [])}
    # Las tareas que ya cubre un skill no reciben atajo nuevo
    cubre = {t: s["nombre"] for s in skills for t in s["tareas"]}
    nuevas = []
    for t in tareas:
        t = dict(t) if isinstance(t, dict) else {"tarea": str(t)}
        if t["tarea"] in cubre and not t.get("skill"):
            t["skill"] = cubre[t["tarea"]]
        nuevas.append(t)
    if tareas:
        resp.setdefault("perfil", {})["tareas"] = nuevas
    resp["skills_existentes"] = bloque
    return resp


def resumen(resp: dict) -> str:
    b = resp.get("skills_existentes") or {}
    ss = b.get("skills", [])
    if not ss:
        return "Tu repositorio no tenía skills previos: no hay nada que revisar."
    def unicos(cond):
        vistos, res = set(), []
        for s in ss:
            for p in s.get("problemas", []):
                texto = p.get("sencillo") or auditar.sencillo(p["que"])
                if cond(p) and (s["nombre"], texto) not in vistos:
                    vistos.add((s["nombre"], texto))
                    res.append((s["nombre"], texto))
        return res

    graves = unicos(lambda p: p["gravedad"] == "alta" and p.get("decision") != "aceptar")
    otros = unicos(lambda p: p["gravedad"] != "alta" and p.get("decision") != "aceptar")
    por_validar = sum(1 for s in ss for d in s.get("conocimiento", []) if d["estado"] == "no verificado")
    out = [f"Encontré {len(ss)} habilidad{'es' if len(ss) != 1 else ''} que ya tenías:"]
    for s in ss:
        cubre = f" Se encarga de: {', '.join(s['tareas'])}." if s.get("tareas") else ""
        para = "no dice para qué sirve" if s["para"].startswith("Sin descripción") else s["para"][:140].rstrip(". ")
        out.append(f"- **{s['nombre']}**: {para}.{cubre}")
    if graves:
        out += ["", "**Lo urgente** (te propongo corregirlo):"]
        out += [f"- **{n}** {texto}." for n, texto in graves]
    if otros:
        out.append("")
        out.append(f"Además hay {len(otros)} detalle{'s' if len(otros) != 1 else ''} menor"
                   f"{'es' if len(otros) != 1 else ''} que te muestro si quieres verlos.")
    if b.get("contradicciones"):
        out.append(f"Hay {len(b['contradicciones'])} punto{'s' if len(b['contradicciones']) != 1 else ''} donde "
                   "las reglas no coinciden; te pregunto cuál vale.")
    if por_validar:
        out.append(f"Voy a comprobar {por_validar} dato{'s' if por_validar != 1 else ''} que usan (normas, "
                   "versiones, cifras) en fuentes oficiales.")
    return "\n".join(out)


def main(argv=None) -> int:
    comun.utf8()
    ap = argparse.ArgumentParser(description="Borrador de la revisión de skills existentes")
    ap.add_argument("--raiz")
    ap.add_argument("--respuestas", default="respuestas-espacio.json")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--borrador", action="store_true")
    g.add_argument("--pendientes", action="store_true")
    g.add_argument("--resumen", action="store_true")
    a = ap.parse_args(argv)
    raiz = comun.encontrar_raiz(a.raiz)
    p = Path(a.respuestas)
    p = p if p.is_absolute() else raiz / p
    try:
        resp = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        resp = None
    if resp is None:
        cfg = comun.leer_config(raiz)
        if cfg is None:
            print("Primero la entrevista: no hay respuestas-espacio.json ni espacio.json.", file=sys.stderr)
            return 2
        resp = {k: cfg[k] for k in ("perfil", "skills_existentes") if k in cfg}
    if a.borrador:
        resp = borrador(raiz, resp)
        comun.escribir(p, json.dumps(resp, ensure_ascii=False, indent=2) + "\n")
        print(resumen(resp))
        return 0
    if a.pendientes:
        for s in (resp.get("skills_existentes") or {}).get("skills", []):
            for d in s.get("conocimiento", []):
                if d["estado"] == "no verificado":
                    print(f"- [{s['nombre']}] {d['dato']}" + (f" (fuente del skill: {d['fuente_en_skill']})"
                                                             if d.get("fuente_en_skill") else ""))
        return 0
    print(resumen(resp))
    return 0


if __name__ == "__main__":
    sys.exit(main())
