#!/usr/bin/env python3
"""Resumen semanal del trabajo de la persona: qué hizo, cuánto tiempo ahorró
con Claude, qué aprendió Claude, qué corrigió, qué quedó pendiente y qué se
repite lo suficiente para volverse atajo.

    (sin argumentos)      los últimos 7 días, en Markdown
    --dias N              otro periodo
    --hasta DD-mmm-YYYY   último día del periodo (por defecto, hoy)
    --proyecto P          solo ese proyecto (en multiproyecto, por defecto todos)
    --guardar             lo guarda como entregable (en multiproyecto, con --proyecto)
    --json

Solo cuenta el trabajo del rol: la bitácora nunca tiene tareas de
configuración. Código de salida: 0 bien, 2 sin espacio o sin dónde guardar.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bitacora  # noqa: E402
import comun  # noqa: E402
import memoria  # noqa: E402


def _marca(raiz: Path) -> Path:
    return raiz / comun.ESTADO / "resumen.json"


def ultimo_resumen(raiz: Path) -> float | None:
    try:
        return float(json.loads(_marca(raiz).read_text(encoding="utf-8"))["ultimo"])
    except (OSError, ValueError, KeyError, TypeError):
        return None


def calcular(raiz: Path, cfg: dict, desde: dt.date, hasta: dt.date, proyecto: str | None) -> dict:
    entradas = []
    for proy, b in bitacora.todas(raiz, cfg):
        if proyecto and proy != proyecto or not b.is_file():
            continue
        for e in bitacora.parsear(b.read_text(encoding="utf-8"))[0]:
            e["proyecto"] = proy
            e["_fecha"] = comun.a_fecha(e.get("fecha", ""))
            entradas.append(e)
    periodo = [e for e in entradas if e["_fecha"] and desde <= e["_fecha"] <= hasta]

    def ahorro(es):
        medidas = [e for e in es if e.get("manual") and e.get("claude")]
        manual = sum(e["manual"] for e in medidas)
        claude = sum(e["claude"] for e in medidas)
        return {"tareas_medidas": len(medidas), "manual": manual, "claude": claude, "ahorro": manual - claude,
                "porcentaje": round(100 * (manual - claude) / manual) if manual else 0}

    por_proceso = {}
    for e in periodo:
        if e.get("proceso") and e.get("manual") and e.get("claude"):
            p = por_proceso.setdefault(e["proceso"], {"veces": 0, "manual": 0, "claude": 0})
            p["veces"] += 1
            p["manual"] += e["manual"]
            p["claude"] += e["claude"]
    nodos = [n for n in memoria.nodos(raiz, cfg)[0]
             if (f := comun.a_fecha(str(n.get("fecha", "")))) and desde <= f <= hasta
             and (not proyecto or n["ambito_carpeta"] in ("global", proyecto))]
    con_atajo = {a["slug"] for a in comun.atajos(cfg) if (raiz / a["ruta"]).is_file()}
    con_atajo |= {d.name for d in (raiz / ".claude" / "skills").glob("*") if d.is_dir()} \
        if (raiz / ".claude" / "skills").is_dir() else set()
    veces = {}
    for e in entradas:
        if e.get("proceso"):
            veces[e["proceso"]] = veces.get(e["proceso"], 0) + 1
    candidatos = sorted(p for p, n in veces.items() if n >= 2 and p not in con_atajo)
    limpio = lambda e: {k: v for k, v in e.items() if not k.startswith("_") and k != "texto"}  # noqa: E731
    return {
        "desde": comun.hoy(desde), "hasta": comun.hoy(hasta), "proyecto": proyecto,
        "tareas": [limpio(e) for e in periodo],
        "tiempo": ahorro(periodo), "tiempo_acumulado": ahorro(entradas),
        "por_proceso": por_proceso,
        "aprendido": [{"id": n.get("id") or n["archivo"].stem, "titulo": n.get("titulo", ""),
                       "tipo": n.get("tipo", "")} for n in nodos],
        "correcciones": [limpio(e) for e in periodo if e.get("correccion")],
        "pendientes": [limpio(e) for e in entradas if e.get("estado") in ("abierta", "parcial")],
        "candidatos_atajo": candidatos,
    }


def markdown(r: dict, cfg: dict) -> str:
    nombre = r["proyecto"] or cfg.get("perfil", {}).get("proyecto", "")
    t, ac = r["tiempo"], r["tiempo_acumulado"]
    out = [f"# Resumen de trabajo — {nombre}", "", f"Del {r['desde']} al {r['hasta']}.", "", "## En números", ""]
    out.append(f"- **Tareas hechas:** {len(r['tareas'])}")
    if t["tareas_medidas"]:
        out.append(f"- **Tiempo con Claude:** {comun.duracion(t['claude'])}")
        out.append(f"- **A mano habrían sido:** {comun.duracion(t['manual'])}")
        out.append(f"- **Tiempo ahorrado:** {comun.duracion(t['ahorro'])} ({t['porcentaje']} %)")
    else:
        out.append("- **Tiempo ahorrado:** sin tareas medidas en este periodo")
    if ac["tareas_medidas"]:
        out.append(f"- **Ahorro acumulado desde el inicio:** {comun.duracion(ac['ahorro'])} "
                   f"en {ac['tareas_medidas']} tareas")
    out += ["", "## Lo que hiciste", ""]
    for e in r["tareas"]:
        tiempos = (f" — {comun.duracion(e['claude'])} con Claude vs. {comun.duracion(e['manual'])} a mano"
                   if e.get("manual") and e.get("claude") else "")
        proy = f" [{e['proyecto']}]" if e.get("proyecto") else ""
        out.append(f"- {e['id']} {e['titulo']}{proy} ({e.get('estado', '')}){tiempos}")
    if not r["tareas"]:
        out.append("- Ninguna tarea registrada en este periodo.")
    if r["por_proceso"]:
        out += ["", "## Dónde más se ahorra", "", "| Tipo de tarea | Veces | Con Claude | A mano | Ahorro |",
                "|---|---|---|---|---|"]
        for p, d in sorted(r["por_proceso"].items(), key=lambda kv: kv[1]["claude"] - kv[1]["manual"]):
            out.append(f"| `{p}` | {d['veces']} | {comun.duracion(d['claude'])} | {comun.duracion(d['manual'])} | "
                       f"{comun.duracion(d['manual'] - d['claude'])} |")
    out += ["", "## Lo que aprendió Claude", ""]
    out += [f"- {n['titulo']} ({n['tipo']})" for n in r["aprendido"]] or ["- Nada nuevo en este periodo."]
    if r["correcciones"]:
        out += ["", "## Lo que corregiste", ""]
        out += [f"- {e['id']} {e['titulo']}" for e in r["correcciones"]]
    if r["pendientes"]:
        out += ["", "## Pendiente", ""]
        out += [f"- {e['id']} {e['titulo']} ({e['estado']})" for e in r["pendientes"]]
    if r["candidatos_atajo"]:
        out += ["", "## Se repite: podría ser un atajo", ""]
        out += [f"- `{p}`" for p in r["candidatos_atajo"]]
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    comun.utf8()
    ap = argparse.ArgumentParser(description="Resumen semanal del trabajo")
    ap.add_argument("--raiz")
    ap.add_argument("--dias", type=int, default=7)
    ap.add_argument("--hasta")
    ap.add_argument("--proyecto")
    ap.add_argument("--guardar", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    raiz = comun.encontrar_raiz(a.raiz)
    cfg = comun.leer_config(raiz)
    if cfg is None:
        print("No hay espacio.json: el espacio no está montado (usa primeros-pasos).", file=sys.stderr)
        return 2
    hasta = comun.a_fecha(a.hasta) if a.hasta else dt.date.today()
    if hasta is None:
        print("--hasta debe ir en formato DD-mmm-YYYY", file=sys.stderr)
        return 2
    desde = hasta - dt.timedelta(days=max(1, a.dias) - 1)
    r = calcular(raiz, cfg, desde, hasta, a.proyecto)
    texto = markdown(r, cfg)
    if a.guardar:
        if comun.proyectos(cfg) and not a.proyecto:
            print("Hay varios proyectos: indica cuál con --proyecto para guardar el resumen.", file=sys.stderr)
            return 2
        carpeta = comun.carpeta_tarea(cfg, a.proyecto, "resumenes", "resumen", comun.hoy(hasta))
        if comun.legado(cfg):
            carpeta = carpeta.rsplit("/", 1)[0]
        destino = raiz / carpeta / f"resumen-{comun.hoy(hasta)}.md"
        comun.escribir(destino, texto)
        r["guardado"] = destino.relative_to(raiz).as_posix()
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print(texto + (f"\nGuardado en {r['guardado']}" if a.guardar else ""))
        comun.escribir(_marca(raiz), json.dumps({"ultimo": time.time()}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
