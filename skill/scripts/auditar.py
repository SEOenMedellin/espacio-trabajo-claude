#!/usr/bin/env python3
"""Revisa los skills, comandos, agentes, reglas, hooks y servidores MCP que ya
trae el repositorio, en busca de problemas de seguridad, de lógica,
contradicciones entre ellos y choques con la arquitectura del espacio.

Es la parte mecánica de la revisión: Claude completa la parte de criterio
(leer cada skill, validar su conocimiento, comparar sus reglas) con
references/skills-existentes.md. Nada se corrige aquí: cada corrección se le
propone a la persona y solo se aplica con su sí.

    (sin argumentos)   informe legible
    --json             hallazgos como lista
    --reglas           reglas de cada fuente («nunca», «siempre», «obligatorio»…),
                       para compararlas entre sí

Código de salida: 0 sin hallazgos graves, 1 hay alguno de gravedad alta.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import activar  # noqa: E402
import comun  # noqa: E402
import inventario  # noqa: E402
import ordenar  # noqa: E402

GRAVEDADES = ("alta", "media", "baja")
INTERNAS = {"scripts", "references", "assets", "templates", "plantillas", "convenciones", "examples", "ejemplos"}

# (patrón, gravedad, qué es, qué hacer)
SEGURIDAD = [
    (r"(?i)\b(api[_-]?key|secret|token|password|passwd|contrase(n|ñ)a)\b\s*[:=]\s*['\"]?([A-Za-z0-9_\-./+=]{16,})",
     "alta", "parece una clave escrita en el archivo",
     "moverla a credenciales/.env y leerla de ahí; rotarla si llegó a git"),
    (r"\b(sk-[A-Za-z0-9]{20,}|gh[pousr]_[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16}|xox[abposr]-[A-Za-z0-9-]{10,}|"
     r"AIza[0-9A-Za-z_\-]{35})", "alta", "clave con formato de un proveedor conocido",
     "sacarla del archivo, rotarla y leerla de credenciales/.env"),
    (r"git\s+push\s+[^\n]*(--force\b|-f\b)", "alta", "push forzado: puede borrar trabajo ajeno",
     "quitar --force o pedir confirmación explícita antes"),
    (r"--no-verify\b", "alta", "salta las verificaciones de git", "quitarlo"),
    (r"git\s+reset\s+--hard", "media", "descarta cambios sin respaldo", "confirmar con la persona antes"),
    (r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*f?\b|Remove-Item[^\n]*-Recurse|shutil\.rmtree", "media",
     "borra carpetas completas", "limitarlo a rutas del skill y confirmar antes de borrar"),
    (r"curl[^\n|]*\|\s*(ba|z)?sh\b|\birm\b[^\n|]*\|\s*iex\b|Invoke-Expression", "media",
     "ejecuta código descargado o generado", "fijar la versión y revisar lo que se ejecuta"),
    (r"\beval\s*\(|\bexec\s*\(", "baja", "ejecuta código dinámico", "revisar que no reciba texto externo"),
    (r"curl\s[^\n]*(-X\s*(POST|PUT|PATCH|DELETE)|--data\b|\s-d\s|\s-F\s|--upload-file)|"
     r"requests\.(post|put|patch|delete)\s*\(|method\s*[:=]\s*['\"](POST|PUT|PATCH|DELETE)['\"]|"
     r"Invoke-(WebRequest|RestMethod)[^\n]*-Method\s+(Post|Put|Patch|Delete)",
     "media", "envía datos a un servicio externo",
     "confirmar a dónde va y que no salgan datos de clientes sin un sí explícito"),
    (r"verify\s*=\s*False|NODE_TLS_REJECT_UNAUTHORIZED\s*=\s*['\"]?0|curl\s[^\n]*\s(-k|--insecure)\b",
     "media", "desactiva la verificación de certificados", "quitarlo"),
    (r"(?i)print\([^)]*(password|token|secret|api_?key)|echo\s+\$\w*(TOKEN|KEY|SECRET|PASS)", "media",
     "puede mostrar una clave en pantalla o en el chat", "no imprimir secretos"),
]
FECHAS = [
    (r"\b(YYYY|AAAA)-(MM)-(DD)\b|\b\d{4}-\d{2}-\d{2}\b", "AAAA-MM-DD"),
    (r"\b(DD|dd)/(MM|mm)/(YYYY|AAAA)\b|\b\d{2}/\d{2}/\d{4}\b", "DD/MM/AAAA"),
    (r"\bDD-mes-(YYYY|AAAA)\b|\b\d{1,2}-(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|"
     r"noviembre|diciembre)-\d{4}\b", "DD-mes completo-AAAA"),
]
# Cómo contárselo a la persona, sin términos técnicos
SENCILLO = [
    ("clave", "tiene una contraseña o clave guardada a la vista"),
    ("push forzado", "al subir cambios puede borrar el trabajo de otras personas"),
    ("verificaciones de git", "se salta los controles al guardar cambios"),
    ("descarta cambios", "puede perder cambios sin guardar copia"),
    ("borra carpetas", "puede borrar carpetas completas"),
    ("código descargado", "ejecuta programas descargados de internet sin revisarlos"),
    ("código dinámico", "ejecuta instrucciones que arma sobre la marcha"),
    ("servicio externo", "envía información fuera de tu equipo"),
    ("certificados", "se conecta a internet sin comprobar que el sitio sea seguro"),
    ("en pantalla", "puede mostrar una clave en pantalla"),
    ("definido", "hay dos habilidades con el mismo nombre y no sé cuál usar"),
    ("sin name o description", "no dice para qué sirve ni cuándo usarla"),
    ("que no existe", "le falta un archivo que necesita"),
    ("no coincide con la carpeta", "su nombre no coincide con su carpeta"),
    ("se activan con", "otra habilidad responde a las mismas palabras"),
    ("también abren primeros-pasos", "responde a las mismas palabras con las que empiezas tu espacio"),
    ("usa fechas", "escribe las fechas de otra forma"),
    ("posible contradicción", "tiene una regla que choca con otra"),
    ("fuera de la arquitectura", "guarda archivos fuera de tus carpetas"),
]


def sencillo(que: str) -> str:
    q = que.lower()
    return next((plano for clave, plano in SENCILLO if clave in q), que.split(": ", 1)[-1])


NEG = re.compile(r"(?i)\b(nunca|jam[aá]s|prohibid[oa]s?|no se (debe|puede)|never|do not|don't|must not)\b")
POS = re.compile(r"(?i)\b(siempre|obligatori[oa]s?|se debe|debe|always|must|required)\b")
VACIAS = set("para como cada esta este estos estas desde donde cuando sobre entre hasta porque pero todo toda todos "
             "todas solo debe deben siempre nunca puede pueden archivo archivos skill skills claude persona the "
             "with that this from into when must never always should".split())


def _textos(raiz: Path, inv: dict) -> list[tuple[str, str, Path]]:
    """[(fuente, tipo, archivo)] de todo lo que hay que revisar."""
    res = []
    repetidos = {n for n in (s["nombre"] for s in inv["skills"]) if [x["nombre"] for x in inv["skills"]].count(n) > 1}
    for s in inv["skills"]:
        fuente = f"{s['nombre']} ({s['ruta']})" if s["nombre"] in repetidos else s["nombre"]
        for a in s["archivos"]:
            f = raiz / s["ruta"] / a
            if f.suffix.lower() in inventario.TEXTO:
                res.append((fuente, "skill", f))
    for clave in ("comandos", "agentes"):
        res += [(x["nombre"], clave[:-1], raiz / x["ruta"]) for x in inv[clave]]
    res += [(r, "reglas", raiz / r) for r in inv["reglas"]]
    return res


def _leer(f: Path) -> str:
    try:
        texto = f.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    if comun.MARCA_INICIO in texto and comun.MARCA_FIN in texto:  # el bloque propio no se audita
        texto = texto.split(comun.MARCA_INICIO, 1)[0] + texto.split(comun.MARCA_FIN, 1)[1]
    return texto


def _linea(texto: str, pos: int) -> int:
    return texto.count("\n", 0, pos) + 1


def _cfg(raiz: Path) -> dict | None:
    cfg = comun.leer_config(raiz)
    if cfg:
        return cfg
    try:
        return json.loads((raiz / "respuestas-espacio.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def frases(descripcion: str) -> set[str]:
    return {activar.normalizar(x) for x in re.findall(r"[\"«“]([^\"»”]{3,40})[\"»”]", descripcion or "")} - {""}


def reglas(raiz: Path, inv: dict) -> dict[str, list[str]]:
    res: dict[str, list[str]] = {}
    for fuente, _, f in _textos(raiz, inv):
        if f.suffix.lower() != ".md":
            continue
        for oracion in re.split(r"(?<=[.!?])\s+|\n\s*[-*]\s+|\n{2,}", _leer(f)):
            o = " ".join(oracion.split())
            if 15 <= len(o) <= 300 and (NEG.search(o) or POS.search(o)):
                res.setdefault(fuente, []).append(o)
    return res


def _claves(o: str) -> set[str]:
    return {w for w in re.findall(r"[a-záéíóúñ]{5,}", o.lower()) if w not in VACIAS}


def auditar(raiz: Path) -> list[dict]:
    inv = inventario.inventario(raiz)
    hall = []

    def h(gravedad, tipo, donde, que, sugerencia=""):
        hall.append({"gravedad": gravedad, "tipo": tipo, "donde": donde, "que": que, "sugerencia": sugerencia,
                     "sencillo": sencillo(que)})

    # Seguridad, en todos los textos y, con más peso, en hooks y MCP (corren solos)
    for fuente, _, f in _textos(raiz, inv):
        texto, rel = _leer(f), f.relative_to(raiz).as_posix()
        for patron, grav, que, sug in SEGURIDAD:
            for m in re.finditer(patron, texto):
                trozo = m.group(0)
                if re.search(r"<|\$\{|\$env|os\.environ|getenv|process\.env|x{4,}|\.{3}|tu[_-]|your[_-]", trozo, re.I):
                    continue
                h(grav, "seguridad", f"{rel}:{_linea(texto, m.start())}", f"{fuente}: {que}", sug)
                break
    for x in inv["hooks"] + inv["mcp"]:
        cmd = x.get("comando", "")
        for patron, grav, que, sug in SEGURIDAD:
            if re.search(patron, cmd):
                donde = x.get("archivo", ".mcp.json")
                h("alta" if grav != "baja" else "media", "seguridad", donde,
                  f"{x.get('evento') or x.get('nombre')}: {que} (corre sin que nadie lo pida)", sug)

    # Lógica
    nombres: dict[str, list[str]] = {}
    for s in inv["skills"]:
        nombres.setdefault(s["nombre"].lower(), []).append(s["ruta"])
        if not s["frontmatter"] or not s["descripcion"]:
            h("media", "logica", f"{s['ruta']}/SKILL.md", f"{s['nombre']}: sin name o description en el encabezado",
              "sin descripción, Claude no sabe cuándo usarlo")
        elif s["nombre"] != s["carpeta"]:
            h("baja", "logica", f"{s['ruta']}/SKILL.md",
              f"{s['nombre']}: el nombre no coincide con la carpeta «{s['carpeta']}»", "igualarlos")
        texto = _leer(raiz / s["ruta"] / "SKILL.md")
        for m in re.finditer(r"`((?:" + "|".join(INTERNAS) + r")/[\w./-]+)`", texto):
            ref = m.group(1).rstrip(".")
            if "*" not in ref and "<" not in ref and not (raiz / s["ruta"] / ref).exists():
                h("media", "logica", f"{s['ruta']}/SKILL.md:{_linea(texto, m.start())}",
                  f"{s['nombre']}: menciona {ref}, que no existe", "crear el archivo o corregir la referencia")
    for x in inv["comandos"] + inv["agentes"]:
        nombres.setdefault(x["nombre"].lower(), []).append(x["ruta"])
    for n, rutas in nombres.items():
        if len(rutas) > 1:
            h("alta", "logica", ", ".join(rutas), f"«{n}» está definido {len(rutas)} veces",
              "dejar uno; Claude no sabe cuál usar")

    # Contradicciones: frases de activación repetidas (incluidas las de este skill)
    propias = frases(inventario.frontmatter(
        (comun.SKILL / "SKILL.md").read_text(encoding="utf-8")).get("description", ""))
    dueno: dict[str, list[str]] = {f: [comun.SKILL.name] for f in propias}
    for s in inv["skills"]:
        for f in frases(s["descripcion"]):
            dueno.setdefault(f, []).append(s["nombre"])
    for frase, quienes in dueno.items():
        if len(set(quienes)) > 1:
            h("media", "contradiccion", ", ".join(sorted(set(quienes))),
              f"varios skills se activan con «{frase}»", "dejar la frase en uno solo")
    for s in inv["skills"]:
        if activar.activa(s["nombre"]) or any(activar.activa(f) for f in frases(s["descripcion"])):
            h("media", "contradiccion", f"{s['ruta']}/SKILL.md",
              f"{s['nombre']}: se activa con palabras que también abren primeros-pasos",
              "cambiar sus frases de activación")

    # Contradicciones: formato de fecha distinto al del espacio
    for fuente, _, f in _textos(raiz, inv):
        texto = _leer(f)
        for patron, nombre in FECHAS:
            m = re.search(patron, texto)
            if m:
                h("baja", "contradiccion", f"{f.relative_to(raiz).as_posix()}:{_linea(texto, m.start())}",
                  f"{fuente}: usa fechas {nombre}; el espacio usa DD-mmm-AAAA (10-oct-2026)",
                  "adaptar el skill o dejar sus salidas en su propia carpeta")
                break

    # Contradicciones: reglas opuestas entre fuentes distintas (posibles; Claude las confirma)
    rs = [(fuente, o, bool(NEG.search(o)), _claves(o)) for fuente, os_ in reglas(raiz, inv).items() for o in os_]
    vistas = 0
    for i, (f1, o1, n1, k1) in enumerate(rs):
        for f2, o2, n2, k2 in rs[i + 1:]:
            if f1 != f2 and n1 != n2 and len(k1 & k2) >= 3 and vistas < 20:
                vistas += 1
                h("baja", "contradiccion", f"{f1} / {f2}",
                  f"posible contradicción: «{o1[:110]}» frente a «{o2[:110]}»", "confirmarlo leyendo ambos")

    # Arquitectura: rutas donde escriben los skills que no caben en el espacio
    cfg = _cfg(raiz)
    if cfg and cfg.get("rutas"):
        est = ordenar.estructura(raiz, cfg)
        for s in inv["skills"]:
            texto = _leer(raiz / s["ruta"] / "SKILL.md")
            for m in re.finditer(r"`([a-zA-Z0-9_<>{}\-]+/[\w<>{}./\-]*)`", texto):
                ruta = m.group(1)
                primero = ruta.split("/")[0]
                if primero.lower() in INTERNAS or primero.startswith((".", "<", "{")) or (raiz / primero).exists():
                    continue
                muestra = re.sub(r"<[^>]*>|\{[^}]*\}", "x", ruta).rstrip("/") or ruta
                motivo = ordenar.evaluar(raiz, cfg, muestra, est, es_dir=ruta.endswith("/"))
                if motivo:
                    h("media", "arquitectura", f"{s['ruta']}/SKILL.md:{_linea(texto, m.start())}",
                      f"{s['nombre']}: usa {ruta}, fuera de la arquitectura ({motivo[:80]})",
                      "adaptar la ruta del skill a la carpeta que le corresponde")
    orden = {g: i for i, g in enumerate(GRAVEDADES)}
    return sorted(hall, key=lambda x: (orden[x["gravedad"]], x["tipo"], x["donde"]))


def main(argv=None) -> int:
    comun.utf8()
    ap = argparse.ArgumentParser(description="Auditoría de skills y reglas existentes")
    ap.add_argument("--raiz")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--reglas", action="store_true")
    a = ap.parse_args(argv)
    raiz = comun.encontrar_raiz(a.raiz)
    if a.reglas:
        rs = reglas(raiz, inventario.inventario(raiz))
        if a.json:
            print(json.dumps(rs, ensure_ascii=False, indent=2))
        else:
            for fuente, os_ in rs.items():
                print(f"\n## {fuente}")
                print("\n".join(f"- {o}" for o in os_))
        return 0
    hall = auditar(raiz)
    if a.json:
        print(json.dumps(hall, ensure_ascii=False, indent=2))
    elif not hall:
        print("Sin hallazgos: no se encontraron problemas de seguridad, lógica, contradicciones ni de arquitectura.")
    else:
        for x in hall:
            print(f"[{x['gravedad']}] {x['tipo']} · {x['donde']}\n    {x['que']}"
                  + (f"\n    qué hacer: {x['sugerencia']}" if x["sugerencia"] else ""))
        cuenta = {g: sum(1 for x in hall if x["gravedad"] == g) for g in GRAVEDADES}
        print("\nResumen: " + ", ".join(f"{n} {g}" for g, n in cuenta.items() if n))
    return 1 if any(x["gravedad"] == "alta" for x in hall) else 0


if __name__ == "__main__":
    sys.exit(main())
