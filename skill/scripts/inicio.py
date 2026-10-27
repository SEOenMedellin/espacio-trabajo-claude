#!/usr/bin/env python3
"""Hook SessionStart: le da a Claude el punto de partida de la sesión.

Lo que imprime entra al contexto de Claude al abrir la sesión:
  1. estado del espacio (si faltan piezas, cómo repararlas) y su orden
     (archivos fuera de la arquitectura o duplicados, vía ordenar.py);
  2. la última sesión de trabajo (las entradas de la fecha más reciente de
     la bitácora de peticiones);
  3. peticiones abiertas o parciales y las más recientes de cada bitácora;
  4. el catálogo de skills instalados (nombre y para qué sirve);
  5. las anotaciones de memoria (id y título de cada nodo).
Y le pide a Claude que, en su primera respuesta, le recuerde a la persona en
dos o tres frases dónde quedó la última sesión.

También registra el inicio de la sesión para cierre_check.py.
Salida acotada (nunca vuelca archivos completos). Cualquier error se traga:
un hook de arranque nunca debe romper la sesión.

Uso manual: python <skill>/scripts/inicio.py   (sin stdin, muestra lo mismo)
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bitacora  # noqa: E402
import comun  # noqa: E402
import grafo  # noqa: E402
import memoria  # noqa: E402
import ordenar  # noqa: E402
import verificar  # noqa: E402
import arranque  # noqa: E402
import resumen  # noqa: E402

MAX_SKILLS = 60
MAX_NODOS = 40


def ultima_sesion(raiz: Path, cfg: dict) -> list[str]:
    """Entradas de la fecha más reciente, en todas las bitácoras de trabajo."""
    todas = []
    for proy, ruta in bitacora.todas(raiz, cfg):
        if ruta.is_file():
            for e in bitacora.parsear(ruta.read_text(encoding="utf-8"))[0]:
                todas.append((proy, e))
    if not todas:
        return []

    def clave(fecha: str) -> tuple:
        try:
            d, m, a = fecha.split("-")
            return int(a), comun.MESES.index(m), int(d)
        except ValueError:
            return (0, 0, 0)

    ultima = max((e.get("fecha", "") for _, e in todas), key=clave)
    out = [f"Fecha: {ultima}"]
    for proy, e in todas:
        if e.get("fecha") == ultima:
            pref = f"[{proy}] " if proy else ""
            resumen = re.sub(r"\*\*[^*]+:\*\*", "", e.get("texto", "")).splitlines()
            linea = next((l.strip() for l in resumen if l.strip()), "")
            out.append(f"  - {pref}{e['id']} — {e['titulo']} ({e.get('estado', '')}): {linea[:160]}")
    return out


def peticiones(raiz: Path, cfg: dict) -> list[str]:
    out = []
    for proy, ruta in bitacora.todas(raiz, cfg):
        if not ruta.is_file():
            continue
        entradas = bitacora.parsear(ruta.read_text(encoding="utf-8"))[0]
        pref = f"[{proy}] " if proy else ""
        abiertas = [e for e in entradas if e.get("estado") in ("abierta", "parcial")]
        for e in abiertas[-5:]:
            out.append(f"  ⚠ {pref}{e['id']} — {e['titulo']} ({e.get('estado')}, {e.get('fecha', '')})")
        for e in [e for e in entradas if e not in abiertas][-3:]:
            out.append(f"  · {pref}{e['id']} — {e['titulo']} ({e.get('fecha', '')})")
    return out


def catalogo(raiz: Path) -> list[str]:
    out = []
    for s in grafo.skills(raiz)[:MAX_SKILLS]:
        desc = s["texto"]
        corte = re.split(r"(?<=[.!?])\s", desc, maxsplit=1)[0] if desc else ""
        out.append(f"  - {s['titulo']}: {corte[:160]}")
    return out


def anotaciones(raiz: Path, cfg: dict) -> list[str]:
    nodos = memoria.nodos(raiz, cfg)[0]
    out = []
    for n in nodos[:MAX_NODOS]:
        amb = "" if n["ambito_carpeta"] == "global" else f" [{n['ambito_carpeta']}]"
        out.append(f"  - {n.get('id', n['archivo'].stem)} ({n.get('tipo', '')}){amb}: {n.get('titulo', '')}")
    if len(nodos) > MAX_NODOS:
        out.append(f"  … y {len(nodos) - MAX_NODOS} más (ver INDICE.md)")
    return out


def main() -> int:
    try:
        payload = json.load(sys.stdin) if not sys.stdin.isatty() else {}
    except ValueError:
        payload = {}
    raiz = comun.encontrar_raiz()
    sid = payload.get("session_id") if isinstance(payload, dict) else None
    if sid:
        comun.sesion_guardar(raiz, sid, {"inicio": time.time(), "avisado": False})
    cfg = comun.leer_config(raiz)
    if cfg is None:
        print("Este espacio todavía no está preparado. Si la persona quiere empezar a trabajar, "
              "usa el skill primeros-pasos (entrevista inicial).")
        return 0
    p = cfg.get("perfil", {})
    print(f"# Inicio de sesión — {p.get('proyecto', '')} · {p.get('cargo', '')}")
    malos = [x for x in verificar.revisar(raiz, cfg) if x[0] in ("FALTA", "DIVERGE")]
    if malos:
        print("Faltan piezas del espacio (" + "; ".join(f"{e} {q}" for e, q, _ in malos[:4])
              + "). Antes de la primera tarea, repáralas con primeros-pasos (montar.py).")
    ps = arranque.pasos(raiz, cfg)
    pendientes = [p for p in ps if not p["ok"]]
    if pendientes:
        print(f"Arranque: {len(ps) - len(pendientes)} de {len(ps)} listo. Falta: "
              + "; ".join(p["que"] for p in pendientes) + ". Muéstraselo a la persona en una línea y, si dice "
              "«sigamos», completa el primero (arranque.py dice cómo; instalar o mover siempre se confirma).")
    marca = raiz / comun.ESTADO / "retiro-ofrecido"
    if not pendientes and comun.activo() and not marca.exists():
        print("El espacio quedó al 100 %. Ofrécele a la persona, una sola vez, retirar el asistente de "
              "configuración (no lo que creó): mantenerlo, desactivarlo o eliminarlo (retirar.py; SKILL.md, "
              "«Retirar el skill»). Explícale en una frase qué cambia con cada opción.")
        comun.escribir(marca, comun.hoy())
    ultimo = resumen.ultimo_resumen(raiz)
    hay_trabajo = any(p["id"] == "primera" and p["ok"] for p in ps)
    if hay_trabajo and (ultimo is None or time.time() - ultimo > 7 * 86400):
        print("Pasó una semana desde el último resumen: ofrécele a la persona su resumen semanal "
              "(resumen.py: qué hizo, tiempo ahorrado, qué aprendió Claude, qué se repite).")
    res = ordenar.escanear(raiz, cfg)
    n, d = len(res["hallazgos"]), len(res["duplicados"])
    if n or d:
        print(f"Orden: {n} elemento(s) fuera de la arquitectura y {d} grupo(s) de duplicados. Menciónalo a la "
              "persona y ofrécele reorganizar: corre ordenar.py, muéstrale el plan archivo por archivo y mueve "
              "solo lo que confirme (ordenar.py --aplicar --solo ...).")
    u = ultima_sesion(raiz, cfg)
    print("\n## Última sesión de trabajo\n" + ("\n".join(u) if u else "(todavía no hay trabajo registrado)"))
    pet = peticiones(raiz, cfg)
    print("\n## Peticiones (⚠ = abiertas o parciales)\n" + ("\n".join(pet) if pet else "  (ninguna todavía)"))
    sk = catalogo(raiz)
    print("\n## Skills disponibles para las tareas\n" + ("\n".join(sk) if sk else "  (ninguno instalado)"))
    an = anotaciones(raiz, cfg)
    print("\n## Anotaciones de memoria\n" + ("\n".join(an) if an else "  (ninguna todavía)"))
    print("\nInstrucción: en tu primera respuesta de esta sesión, recuérdale a la persona en dos o tres "
          "frases dónde quedó la última sesión y, si hay peticiones abiertas, pregúntale si las retoma. "
          "Para cada tarea, usa este catálogo de skills y corre grafo.py --plan antes de actuar.")
    return 0


if __name__ == "__main__":
    comun.utf8()
    try:
        sys.exit(main())
    except Exception:  # noqa: BLE001
        sys.exit(0)
