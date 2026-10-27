#!/usr/bin/env python3
"""Grafo de orquestación: cruza skills, memoria, contexto, investigaciones y
peticiones anteriores para decir qué abrir antes de resolver una petición.

    --plan "<petición>"  qué skills invocar, qué nodos de memoria leer, qué
                         documentos de contexto e investigaciones previas
                         aplican, y qué peticiones parecidas ya se resolvieron.
    --actualizar         reconstruye .espacio/grafo.json (nodos y aristas).

El grafo es derivado: si diverge del disco, gana el disco. La búsqueda es por
palabras (sin acentos, con raíz de 6 letras), no semántica: si el plan no
encuentra nada, eso también es información (toca investigar).

Uso (desde la raíz):
    python <skill>/scripts/grafo.py --plan "texto" [--proyecto P] [--json]
    python <skill>/scripts/grafo.py --actualizar

Código de salida: 0 bien, 2 no hay espacio.json.
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
import memoria  # noqa: E402

VACIAS = set("""a al algo ante con contra de del desde donde el ella ellos en entre era es esa ese eso esta este
esto estos fue ha hay la las le les lo los mas me mi mis muy necesito no nos o para pero por que quiero se ser si
sin sobre su sus te tu un una uno unos y ya hacer haz dame puedes favor como cual cuales the and for with from this
that to of in on is are be by an or it as at""".split())
TEXTO = {".md", ".txt", ".csv", ".json", ".yaml", ".yml", ".html", ".py", ".feature"}


def raices(texto: str) -> set[str]:
    palabras = re.findall(r"[a-z0-9]+", comun.sin_acentos(texto).lower())
    return {w[:6] for w in palabras if len(w) >= 3 and w not in VACIAS}


def leer(p: Path, limite: int = 1500) -> str:
    if p.suffix.lower() not in TEXTO:
        return ""
    try:
        return p.read_text(encoding="utf-8", errors="replace")[:limite]
    except OSError:
        return ""


def skills(raiz: Path) -> list[dict]:
    res = []
    carpeta = raiz / ".claude" / "skills"
    if not carpeta.is_dir():
        return res
    for f in sorted(carpeta.glob("*/SKILL.md")):
        texto = leer(f, 4000)
        nombre, desc = f.parent.name, ""
        if texto.startswith("---"):
            cab = texto.split("---", 2)[1] if texto.count("---") >= 2 else ""
            m = re.search(r"^name:\s*(.+)$", cab, re.M)
            if m:
                nombre = m.group(1).strip().strip("'\"")
            m = re.search(r"^description:\s*(.*?)(?=^\S[\w-]*:|\Z)", cab, re.M | re.S)
            if m:
                desc = " ".join(m.group(1).replace(">", " ").replace("|", " ").split()).strip("'\"")
        res.append({"tipo": "skill", "id": f"skill:{nombre}", "titulo": nombre, "texto": desc,
                    "ruta": f.relative_to(raiz).as_posix()})
    return res


def archivos(raiz: Path, carpeta: Path, tipo: str) -> list[dict]:
    res = []
    if not carpeta.is_dir():
        return res
    for f in sorted(carpeta.rglob("*")):
        if not f.is_file() or f.name in (".gitkeep", "INDICE.md") or "__pycache__" in f.parts:
            continue
        rel = f.relative_to(raiz).as_posix()
        res.append({"tipo": tipo, "id": f"{tipo}:{rel}", "titulo": f.stem.replace("-", " ").replace("_", " "),
                    "texto": leer(f), "ruta": rel})
    return res


def recolectar(raiz: Path, cfg: dict, proyecto: str | None = None) -> list[dict]:
    items = skills(raiz)
    for n in memoria.nodos(raiz, cfg)[0]:
        if proyecto and n["ambito_carpeta"] not in ("global", proyecto):
            continue
        items.append({"tipo": "memoria", "id": f"memoria:{n.get('id', n['archivo'].stem)}",
                      "titulo": n.get("titulo", ""), "texto": " ".join(n.get("tags") or []) + " " + n["cuerpo"][:1500],
                      "ruta": n["archivo"].relative_to(raiz).as_posix(), "enlaces": n["enlaces"]})
    lista = [proyecto] if proyecto else (comun.proyectos(cfg) or [None])
    for p in lista:
        r = comun.resolver(cfg, p)
        for rol, tipo in (("contexto", "contexto"), ("investigacion", "investigacion")):
            if r.get(rol) and "<proyecto>" not in r[rol]:
                items += archivos(raiz, raiz / comun.base_dir(r[rol]), tipo)
    for p, ruta in bitacora.todas(raiz, cfg):
        if proyecto and p and p != proyecto:
            continue
        if not ruta.is_file():
            continue
        for e in bitacora.parsear(ruta.read_text(encoding="utf-8"))[0]:
            items.append({"tipo": "peticion", "id": f"peticion:{p + '/' if p else ''}{e['id']}",
                          "titulo": e.get("titulo", ""), "texto": e.get("texto", "") + " " + e.get("proceso", ""),
                          "ruta": ruta.relative_to(raiz).as_posix(), "skills": e.get("skills", []),
                          "memoria": e.get("memoria", []), "archivos": e.get("archivos", []),
                          "proceso": e.get("proceso", ""), "estado": e.get("estado", "")})
    return items


def puntuar(items: list[dict], peticion: str) -> list[tuple[float, dict]]:
    q = raices(peticion)
    res = []
    for it in items:
        en_titulo = q & raices(it["titulo"])
        en_texto = q & raices(it["texto"])
        s = 3.0 * len(en_titulo) + 1.0 * len(en_texto - en_titulo)
        if s > 0:
            res.append((s, it))
    return sorted(res, key=lambda x: -x[0])


def plan(raiz: Path, cfg: dict, peticion: str, proyecto: str | None) -> dict:
    items = recolectar(raiz, cfg, proyecto)
    puntos = puntuar(items, peticion)
    umbral = 3.0

    def top(tipo: str, n: int) -> list[dict]:
        return [dict(it, puntaje=s) for s, it in puntos if it["tipo"] == tipo and s >= umbral][:n]

    previas = top("peticion", 3)
    sk = top("skill", 3)
    heredadas = {s for p in previas for s in p.get("skills", [])}
    ya = {x["titulo"] for x in sk}
    for nombre in sorted(heredadas - ya):
        ruta = next((it["ruta"] for it in items if it["tipo"] == "skill" and it["titulo"] == nombre), "")
        sk.append({"titulo": nombre, "ruta": ruta, "puntaje": 0, "texto": "usado en una petición parecida"})
    mem = top("memoria", 5)
    ids_mem = {m["id"] for m in mem}
    for p in previas:
        for m in p.get("memoria", []):
            if f"memoria:{m}" not in ids_mem:
                it = next((x for x in items if x["id"] == f"memoria:{m}"), None)
                if it:
                    mem.append(dict(it, puntaje=0))
                    ids_mem.add(it["id"])
    r = comun.resolver(cfg, proyecto)
    return {"peticion": peticion, "proyecto": proyecto, "skills": sk, "memoria": mem,
            "contexto": top("contexto", 5), "investigaciones": top("investigacion", 3), "peticiones": previas,
            "carpeta_contexto": r.get("contexto", ""),
            "sin_antecedentes": not (sk or mem or previas or top("investigacion", 1))}


def imprimir_plan(pl: dict) -> None:
    print(f"PLAN — «{pl['peticion']}»" + (f"  (proyecto: {pl['proyecto']})" if pl["proyecto"] else ""))
    print("=" * 70)

    def bloque(titulo: str, lista: list[dict], extra=lambda x: "") -> None:
        print(f"\n## {titulo}")
        if not lista:
            print("  (nada)")
        for x in lista:
            print(f"  • {x['titulo']}  —  {x.get('ruta', '')}{extra(x)}")

    bloque("1. Skills a invocar (con la herramienta Skill)", pl["skills"],
           lambda x: f"\n      {x['texto'][:140]}" if x.get("texto") else "")
    bloque("2. Memoria a leer", pl["memoria"])
    print(f"\n## 3. Contexto — listar completo: {pl['carpeta_contexto'] or '(sin rol contexto)'}")
    for x in pl["contexto"]:
        print(f"  • {x['ruta']}")
    bloque("4. Investigaciones previas", pl["investigaciones"])
    bloque("5. Peticiones parecidas ya resueltas", pl["peticiones"],
           lambda x: f"  [{x.get('proceso', '')} · {x.get('estado', '')}]"
                     + (f"\n      archivos: {', '.join(x['archivos'][:4])}" if x.get("archivos") else ""))
    if pl["sin_antecedentes"]:
        print("\nSin antecedentes: no hay skill, memoria ni petición previa que aplique. "
              "Aplica el protocolo de investigación (docs/espacio-de-trabajo/investigacion.md).")


def actualizar(raiz: Path, cfg: dict) -> str:
    items = recolectar(raiz, cfg)
    nodos = [{k: it[k] for k in ("id", "tipo", "titulo", "ruta")} for it in items]
    ids = {n["id"] for n in nodos}
    aristas = []
    for it in items:
        if it["tipo"] == "peticion":
            for s in it.get("skills", []):
                aristas.append({"de": it["id"], "a": f"skill:{s}", "rel": "usa"})
            for m in it.get("memoria", []):
                aristas.append({"de": it["id"], "a": f"memoria:{m}", "rel": "usa"})
            for f in it.get("archivos", []):
                aristas.append({"de": it["id"], "a": f"archivo:{f}", "rel": "entrega"})
        if it["tipo"] == "memoria":
            for e in it.get("enlaces", []):
                aristas.append({"de": it["id"], "a": f"memoria:{e}", "rel": "relacionado"})
    huerfanas = sorted({a["a"] for a in aristas if a["a"] not in ids and not a["a"].startswith("archivo:")})
    destino = raiz / comun.ESTADO / "grafo.json"
    comun.escribir(destino, json.dumps({"generado": comun.hoy(), "nodos": nodos, "aristas": aristas,
                                        "referencias_rotas": huerfanas}, ensure_ascii=False, indent=1))
    cuenta = {}
    for n in nodos:
        cuenta[n["tipo"]] = cuenta.get(n["tipo"], 0) + 1
    resumen = ", ".join(f"{v} {k}" for k, v in sorted(cuenta.items())) or "vacío"
    aviso = f" · {len(huerfanas)} referencia(s) rota(s): {', '.join(huerfanas[:5])}" if huerfanas else ""
    return f"grafo actualizado: {resumen}, {len(aristas)} aristas{aviso}"


def main(argv=None) -> int:
    comun.utf8()
    ap = argparse.ArgumentParser(description="Grafo de orquestación")
    ap.add_argument("--raiz")
    ap.add_argument("--plan")
    ap.add_argument("--proyecto")
    ap.add_argument("--actualizar", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    raiz = comun.encontrar_raiz(a.raiz)
    cfg = comun.leer_config(raiz)
    if cfg is None:
        print("No hay espacio.json: el espacio no está montado (usa primeros-pasos).", file=sys.stderr)
        return 2
    if a.proyecto and a.proyecto not in comun.proyectos(cfg):
        print(f"Proyecto desconocido: {a.proyecto}. Disponibles: {', '.join(comun.proyectos(cfg)) or '—'}",
              file=sys.stderr)
        return 2
    if a.actualizar:
        print(actualizar(raiz, cfg))
    if a.plan:
        pl = plan(raiz, cfg, a.plan, a.proyecto)
        if a.json:
            print(json.dumps(pl, ensure_ascii=False, indent=2))
        else:
            imprimir_plan(pl)
    if not (a.actualizar or a.plan):
        ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
