"""Prueba de punta a punta de primeros-pasos.

Monta dos espacios en una carpeta temporal (un proyecto con código previo, y
varios proyectos) y recorre: validación de respuestas, montaje, idempotencia,
memoria, bitácora, grafo, hooks (inicio, cierre, orden), límites de ruta,
reorganización y ampliación.

    python tests/prueba_completa.py          # salida completa
    python tests/prueba_completa.py -q       # solo el resultado

Sale con código 1 si algo falla. Solo biblioteca estándar, Python 3.10+.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

for _f in (sys.stdout, sys.stderr):
    try:
        _f.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

SKILL = Path(__file__).resolve().parents[1] / "skill"
sys.path.insert(0, str(SKILL / "scripts"))
import comun  # noqa: E402
BASE = Path(tempfile.mkdtemp(prefix="pp-"))
SILENCIO = "-q" in sys.argv
fallos = []


def log(texto):
    if not SILENCIO:
        print(texto)


def run(repo, args, stdin=None, esperado=None):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(repo))
    r = subprocess.run([sys.executable, str(repo / ".claude/skills/primeros-pasos/scripts" / args[0]), *args[1:]],
                       cwd=repo, input=stdin, capture_output=True, text=True, encoding="utf-8", env=env)
    log(f"\n$ {' '.join(args)}  → {r.returncode}")
    log((r.stdout + r.stderr).strip()[:2500])
    if esperado is not None and r.returncode != esperado:
        fallos.append(f"{args} devolvió {r.returncode}, esperaba {esperado}")
    return r


def bitacora_entradas(repo_):
    sys.path.insert(0, str(SKILL / "scripts"))
    import bitacora as _b
    return _b.parsear((repo_ / "bitacora-peticiones.md").read_text(encoding="utf-8"))[0]


def repo(nombre):
    d = BASE / nombre
    shutil.copytree(SKILL, d / ".claude/skills/primeros-pasos", ignore=shutil.ignore_patterns("__pycache__"))
    return d


def write(repo_, ruta):
    return run(repo_, ["orden_check.py"], stdin=json.dumps({"tool_name": "Write", "tool_input": {
        "file_path": str(repo_ / ruta), "content": "x"}}), esperado=0).stdout


ROL = {
    "fecha": "27-oct-2026", "rol": "Analista de operaciones",
    "responsabilidades": ["Medir el cumplimiento de entregas"],
    "obligaciones": ["Conservar los datos fuente de cada indicador"],
    "tareas_comunes": ["Cierre mensual de indicadores"],
    "lineamientos": [{"regla": "Los exportes originales no se modifican", "por_que": "Cada indicador debe poder rehacerse",
                      "aplica_en": "datos/crudos/"}],
    "supuestos": [], "fuentes": [{"titulo": "Clasificación de ocupaciones", "url": "https://ejemplo.org/ocupaciones",
                                  "consultado": "27-oct-2026"}],
}

# ---------- Repo A: un proyecto, análisis de datos, con código previo
A = repo("a")
(A / "src").mkdir()
(A / "src/main.py").write_text("print(1)\n")
(A / "README.md").write_text("# Repo previo\n")
(A / ".claude/settings.json").write_text(json.dumps({"hooks": {"PostToolUse": [{"matcher": "*", "hooks": [
    {"type": "command", "command": "telemetria emit"}]}]}}))
resp = {
    "idioma": "es", "trato": "Directo y sin tecnicismos.", "git": False,
    "perfil": {"cargo": "Analista de operaciones", "area": "Operaciones", "proyecto": "Tablero logístico",
               "objetivo": "Indicadores semanales de cumplimiento de entregas.", "destinatarios": "Gerencia",
               "conocimientos": ["OTIF y lead time", "Limpieza de datos"],
               "tareas": [{"tarea": "Actualizar el tablero semanal", "frecuencia": "semanal", "entrega": "tablero"}],
               "herramientas": ["Hoja de cálculo", "Sistema de gestión"]},
    "arquitectura": {"tipo": "analisis-de-datos", "modo": "unico", "por_que": "Exportes del ERP a indicadores.",
                     "carpetas": [{"ruta": "datos/crudos/", "para": "Exportes originales"},
                                  {"ruta": "datos/procesados/", "para": "Datos limpios"},
                                  {"ruta": "analisis/", "para": "Consultas y scripts"}]},
    "rutas": {"contexto": "contexto/", "entregables": "reportes/", "investigacion": "investigacion/",
              "memoria_global": "memoria/", "bitacora_peticiones": "bitacora-peticiones.md"},
    "credenciales": [{"variable": "ERP_USUARIO", "para": "Usuario de solo lectura"}],
    "programas": [{"nombre": "Programa ausente", "para": "Correr el análisis",
                   "comprobar": "programa-que-no-existe-pp --version", "instalar": "https://ejemplo.org/descargas"}],
    "investigacion_rol": ROL,
}
(A / "respuestas-espacio.json").write_text(json.dumps(resp, ensure_ascii=False), encoding="utf-8")
run(A, ["verificar.py"], esperado=2)
malo = dict(resp, credenciales=[{"variable": "erp", "valor": "x"}])
(A / "malo.json").write_text(json.dumps(malo), encoding="utf-8")
run(A, ["montar.py", "--respuestas", "malo.json", "--dry-run"], esperado=2)
profundo = json.loads(json.dumps(resp))
profundo["arquitectura"]["carpetas"].append({"ruta": "a/b/c/d/e/", "para": "demasiado profundo"})
(A / "malo.json").write_text(json.dumps(profundo), encoding="utf-8")
run(A, ["montar.py", "--respuestas", "malo.json", "--dry-run"], esperado=2)
# la investigación del rol es obligatoria al montar, con fuentes o con su limitación
for malo, nota in [({k: v for k, v in resp.items() if k != "investigacion_rol"}, "sin investigación del rol"),
                   (dict(resp, investigacion_rol=dict(ROL, fuentes=[])), "sin fuentes ni limitación"),
                   (dict(resp, investigacion_rol=dict(ROL, lineamientos=[{"regla": "x"}])), "lineamiento sin por_que"),
                   (dict(resp, programas=[{"nombre": "x", "para": "y"}]), "programa sin comprobar")]:
    (A / "malo.json").write_text(json.dumps(malo, ensure_ascii=False), encoding="utf-8")
    if run(A, ["montar.py", "--respuestas", "malo.json", "--dry-run"]).returncode != 2:
        fallos.append(f"montar aceptó respuestas {nota}")
(A / "malo.json").write_text(json.dumps(dict(resp, investigacion_rol=dict(
    ROL, fuentes=[], limitacion="Sin acceso a internet"))), encoding="utf-8")
run(A, ["montar.py", "--respuestas", "malo.json", "--dry-run"], esperado=0)
(A / "malo.json").unlink()
run(A, ["montar.py", "--respuestas", "respuestas-espacio.json", "--dry-run"], esperado=0)
run(A, ["montar.py", "--respuestas", "respuestas-espacio.json"], esperado=0)
if (A / "respuestas-espacio.json").exists():
    fallos.append("montar no borró respuestas-espacio.json")
if (A / "BITACORA.md").exists():
    fallos.append("el montaje creó BITACORA.md: lo del sistema no se registra")
r = run(A, ["verificar.py"], esperado=0)
if "AVISO" not in r.stdout or "Programa ausente" not in r.stdout:
    fallos.append("verificar no avisó del programa que falta")
doc_rol = A / "investigacion/27-oct-2026-rol-analista-de-operaciones.md"
if not doc_rol.is_file() or "ejemplo.org/ocupaciones" not in doc_rol.read_text(encoding="utf-8"):
    fallos.append("montar no guardó la investigación del rol con sus fuentes")
for f in ("CLAUDE.md", "docs/espacio-de-trabajo/perfil.md"):
    if "Los exportes originales no se modifican" not in (A / f).read_text(encoding="utf-8"):
        fallos.append(f"{f} no lleva los lineamientos del rol")
if "Programa ausente" not in (A / "docs/espacio-de-trabajo/perfil.md").read_text(encoding="utf-8"):
    fallos.append("perfil.md no lista los programas")
r = run(A, ["programas.py", "--json"])
nombres = [x["nombre"] for x in json.loads(r.stdout or "[]")]
if nombres[:3] != ["python", "node", "playwright"] or "Programa ausente" not in nombres:
    fallos.append(f"programas.py no lista los de base y los del espacio: {nombres}")
if r.returncode != 1:
    fallos.append("programas.py no avisa con código 1 cuando falta un programa")
run(A, ["programas.py", "--comando", "no-existe"], esperado=2)
run(A, ["programas.py", "--comando", "python"], esperado=0)
if "Programa ausente" not in run(A, ["inicio.py"], stdin="{}").stdout:
    fallos.append("el aviso de inicio no dice qué programas faltan")
r = run(A, ["montar.py"], esperado=0)
if "creado" in r.stdout.replace("ya existía", ""):
    fallos.append("montar no es idempotente")
st = json.loads((A / ".claude/settings.json").read_text())
if "telemetria" not in json.dumps(st) or "orden_check" not in json.dumps(st):
    fallos.append("settings no conservó la telemetría o no agregó hooks")
if "activar.py" not in json.dumps(st.get("hooks", {}).get("UserPromptSubmit", [])):
    fallos.append("montar no registró el hook de activación")

# activación con «empezar», «iniciar», «configurar»…
for texto, debe in [("empezar", True), ("Iniciar", True), ("¡Empecemos!", True), ("configurar", True),
                    ("configura mi espacio", True), ("hola, quiero empezar", True), ("primeros pasos", True),
                    ("soy nuevo en el proyecto", True), ("setup", True), ("configura el linter", False),
                    ("empezar el informe mensual", False), ("inicia sesión en el CRM", False),
                    ("voy a iniciar el análisis de ventas", False)]:
    salida = run(A, ["activar.py"], stdin=json.dumps({"prompt": texto}), esperado=0).stdout
    if ("primeros-pasos" in salida) != debe:
        fallos.append(f"activar.py con {texto!r}: esperaba {'activar' if debe else 'no activar'}")
cfg = json.loads((A / "espacio.json").read_text(encoding="utf-8"))
if sorted(cfg["arquitectura"]["preexistentes"]) != ["README.md", "src"]:
    fallos.append(f"preexistentes inesperados: {cfg['arquitectura']['preexistentes']}")

# atajos y lista de arranque
atajo = A / ".claude/skills/actualizar-el-tablero-semanal/SKILL.md"
if not atajo.is_file() or "name: actualizar-el-tablero-semanal" not in atajo.read_text(encoding="utf-8"):
    fallos.append("montar no creó el atajo de la tarea habitual")
elif "tarea.py --empezar --proceso actualizar-el-tablero-semanal" not in atajo.read_text(encoding="utf-8"):
    fallos.append("el atajo no pone en marcha el reloj de la tarea")
r = run(A, ["arranque.py", "--json"], esperado=1)
pasos_ok = {x["id"]: x["ok"] for x in json.loads(r.stdout)["pasos"]}
if not pasos_ok.get("atajos") or pasos_ok.get("primera") or pasos_ok.get("programas"):
    fallos.append(f"arranque no refleja el estado: {pasos_ok}")
if "Arranque:" not in run(A, ["inicio.py"], stdin="{}").stdout:
    fallos.append("el aviso de inicio no muestra la lista de arranque")

# reloj de la tarea
run(A, ["tiempo.py", "--empezar", "tablero-semanal"], esperado=0)
r = run(A, ["tiempo.py", "--terminar", "--json"], esperado=0)
medida = json.loads(r.stdout)
if medida.get("desde") != "tarea" or not medida.get("minutos"):
    fallos.append(f"tiempo.py no midió la tarea: {medida}")
run(A, ["tiempo.py", "--estimacion", "tablero-semanal"], esperado=1)

# memoria + bitácora + grafo
(A / "memoria/otif-se-calcula-por-pedido.md").write_text(
    "---\nid: otif-se-calcula-por-pedido\ntitulo: El OTIF se calcula por pedido, no por línea\ntipo: decision\n"
    "ambito: global\nfecha: 27-oct-2026\ntags: [otif, indicadores]\nrelacionado: []\n---\nCuerpo.\n",
    encoding="utf-8")
run(A, ["memoria.py", "--rebuild"], esperado=0)
r = run(A, ["bitacora.py", "--siguiente"], esperado=0)
if r.stdout.strip() != "P-001":
    fallos.append(f"bitacora --siguiente dio {r.stdout.strip()!r}, esperaba P-001")
b = A / "bitacora-peticiones.md"
t = b.read_text(encoding="utf-8").replace("## Entradas\n", "## Entradas\n\n### P-001 — Tablero semanal de OTIF\n"
    "<!-- fecha: 27-oct-2026 | skills: | memoria: otif-se-calcula-por-pedido | archivos: reportes/x.md | "
    "proceso: tablero-semanal | estado: parcial | manual: 120 | claude: 25 -->\n\n**Petición:** actualizar tablero OTIF.\n\n"
    "**Cómo se resolvió:** con el exporte.\n\n**Conocimiento adyacente:** el ERP corta a medianoche UTC.\n\n")
b.write_text(t, encoding="utf-8")
run(A, ["bitacora.py", "--tabla"], esperado=0)
run(A, ["bitacora.py"], esperado=0)
# tiempo ahorrado: un minuto que no es número se rechaza
segunda = ("### P-002 — Tablero de la semana 2\n<!-- fecha: 26-oct-2026 | skills: | memoria: | archivos: | "
           "proceso: tablero-semanal | estado: resuelta | manual: dos | claude: 10 -->\n\n**Petición:** otra vez."
           "\n\n**Cómo se resolvió:** igual.\n\n")
t = b.read_text(encoding="utf-8").replace("## Procesos candidatos", segunda + "## Procesos candidatos", 1)
b.write_text(t, encoding="utf-8")
run(A, ["bitacora.py"], esperado=1)
b.write_text(t.replace("manual: dos", "manual: 60"), encoding="utf-8")
run(A, ["bitacora.py"], esperado=0)
if "1 h" not in run(A, ["tiempo.py", "--estimacion", "tablero-semanal"], esperado=0).stdout:
    fallos.append("tiempo.py no propone la última estimación manual")
# resumen semanal
r = run(A, ["resumen.py", "--json", "--hasta", "27-oct-2026"], esperado=0)
res = json.loads(r.stdout)
if (res["tiempo"]["manual"], res["tiempo"]["claude"], res["tiempo"]["ahorro"]) != (180, 35, 145):
    fallos.append(f"resumen calculó mal el tiempo: {res['tiempo']}")
if len(res["tareas"]) != 2 or "tablero-semanal" not in res["candidatos_atajo"]:
    fallos.append(f"resumen: tareas o candidatos inesperados: {len(res['tareas'])}, {res['candidatos_atajo']}")
if not any(n["id"] == "otif-se-calcula-por-pedido" for n in res["aprendido"]):
    fallos.append("resumen no muestra lo que aprendió Claude")
if len(json.loads(run(A, ["resumen.py", "--json", "--hasta", "27-oct-2026", "--dias", "1"]).stdout)["tareas"]) != 1:
    fallos.append("resumen no filtra por periodo")
r = run(A, ["resumen.py", "--hasta", "27-oct-2026", "--guardar"], esperado=0)
if "Te ahorraste" in r.stdout or "2 h 25 min" not in r.stdout:
    fallos.append("el resumen no muestra el ahorro en horas y minutos")
if not (A / "reportes/resumenes/resumen-27-oct-2026/resumen-27-oct-2026.md").is_file():
    fallos.append("resumen --guardar no dejó el entregable")
if "resumen semanal" in run(A, ["inicio.py"], stdin="{}").stdout:
    fallos.append("el aviso de inicio ofrece el resumen aunque se acaba de ver")
if not {x["id"]: x["ok"] for x in json.loads(run(A, ["arranque.py", "--json"]).stdout)["pasos"]}["primera"]:
    fallos.append("la primera tarea no cuenta en la lista de arranque")
run(A, ["grafo.py", "--actualizar"], esperado=0)
r = run(A, ["grafo.py", "--plan", "actualizar el tablero de OTIF de esta semana"], esperado=0)
if "otif-se-calcula-por-pedido" not in r.stdout or "Tablero semanal de OTIF" not in r.stdout:
    fallos.append("el plan no encontró la memoria o la petición previa")
r = run(A, ["grafo.py", "--plan", "redactar un contrato de arrendamiento"], esperado=0)
if "Sin antecedentes" not in r.stdout:
    fallos.append("el plan no marcó 'sin antecedentes'")

# abrir y cerrar una tarea: carpeta por tarea, memoria.md, hora y grafo tipado
(A / "memoria/tablero-desde-exporte.md").write_text(
    "---\nid: tablero-desde-exporte\ntitulo: El tablero se arma desde el exporte\ntipo: proceso\nambito: global\n"
    "fecha: 27-oct-2026\ntags: [tablero]\nrelacionado: [requiere:otif-se-calcula-por-pedido]\n---\nCuerpo.\n",
    encoding="utf-8")
r = run(A, ["tarea.py", "--empezar", "--proceso", "tablero-semanal", "--categoria", "informes", "--json"], esperado=0)
t = json.loads(r.stdout)
if t["carpeta"] != f"reportes/informes/{t['id']}-{comun.hoy()}" or not (A / t["carpeta"]).is_dir():
    fallos.append(f"tarea.py no creó la carpeta de la tarea: {t}")
(A / t["carpeta"] / "tablero.md").write_text("# Tablero\n", encoding="utf-8")
cierre = {"titulo": "Tablero de la semana 3", "peticion": "Actualizar el tablero.", "como": "Con el exporte.",
          "patrones": "Filtrar devoluciones primero.", "memoria": ["tablero-desde-exporte"],
          "deriva_en": ["otif-se-calcula-por-pedido"], "manual": 90}
r = run(A, ["tarea.py", "--cerrar", "--datos", "-"], stdin=json.dumps(cierre), esperado=0)
if "Te ahorraste" not in r.stdout:
    fallos.append(f"tarea.py no dijo el tiempo ahorrado: {r.stdout!r}")
entrada = [e for e in bitacora_entradas(A) if e["id"] == t["id"]]
if not entrada or not re.match(r"^\d{2}:\d{2}$", entrada[0].get("hora", "")) or entrada[0].get("manual") != 90:
    fallos.append(f"la entrada de la bitácora no tiene hora o tiempos: {entrada}")
elif entrada[0].get("archivos") != [f"{t['carpeta']}/tablero.md"]:
    fallos.append(f"la entrada no registró el entregable: {entrada[0].get('archivos')}")
mem = A / t["carpeta"] / "memoria.md"
if not mem.is_file() or "Filtrar devoluciones" not in mem.read_text(encoding="utf-8") \
        or "resuelve → proceso" not in mem.read_text(encoding="utf-8"):
    fallos.append("tarea.py no dejó memoria.md con lo aprendido y sus relaciones")
run(A, ["bitacora.py"], esperado=0)
g = json.loads((A / ".espacio/grafo.json").read_text(encoding="utf-8"))
rels = {(a["de"].split(":", 1)[0], a["rel"], a["a"].split(":", 1)[0]) for a in g["aristas"]}
for esperado in [("peticion", "requiere", "memoria"), ("peticion", "resuelve", "proceso"),
                 ("peticion", "deriva_en", "archivo"), ("peticion", "deriva_en", "memoria"),
                 ("memoria", "requiere", "memoria")]:
    if esperado not in rels:
        fallos.append(f"el grafo no tiene la relación tipada {esperado}")
gm = A / "docs/espacio-de-trabajo/graph.md"
if not gm.is_file() or "resuelve →" not in gm.read_text(encoding="utf-8"):
    fallos.append("no se generó graph.md con relaciones legibles")
if "## Validaciones" not in (A / ".claude/skills/actualizar-el-tablero-semanal/SKILL.md").read_text(encoding="utf-8"):
    fallos.append("el atajo no tiene sección Validaciones")

# hooks de inicio y cierre
r = run(A, ["inicio.py"], stdin=json.dumps({"session_id": "s1"}), esperado=0)
for parte in ("Última sesión de trabajo", "P-001", "Skills disponibles", "otif-se-calcula-por-pedido"):
    if parte not in r.stdout:
        fallos.append(f"inicio.py no muestra {parte!r}")
run(A, ["cierre_check.py"], stdin=json.dumps({"session_id": "s1"}), esperado=0)
(A / "reportes/informes/P-009-27-oct-2026").mkdir(parents=True)
(A / "reportes/informes/P-009-27-oct-2026/semana.md").write_text("x")
r = run(A, ["cierre_check.py"], stdin=json.dumps({"session_id": "s1"}), esperado=0)
if '"block"' not in r.stdout:
    fallos.append("cierre_check no bloqueó con cambios sin bitácora")
r = run(A, ["cierre_check.py"], stdin=json.dumps({"session_id": "s1"}), esperado=0)
if r.stdout.strip():
    fallos.append("cierre_check avisó dos veces")

# hook de orden: escrituras y movimientos
largo = "x" * 70
for ruta, debe in [("informe.md", "deny"), ("reportes/informe.md", "deny"), ("cosas/a.md", "deny"),
                   ("analisis/Mi Consulta.sql", "deny"), ("analisis/a/b/c/d/e/f.sql", "deny"),
                   (f"reportes/informes/P-001-27-oct-2026/{largo}.md", "deny"),
                   ("reportes/informes/b.md", "deny"), ("reportes/27-oct-2026/informes/b.md", "deny"),
                   ("reportes/informes/P-001-27-oct-2026/b.md", ""), ("memoria/nuevo-nodo.md", ""),
                   ("contexto/Brief Cliente.pdf", ""), ("src/nuevo.py", ""),
                   (".claude/skills/x/SKILL.md", ""), ("README.md", "")]:
    salida = write(A, ruta)
    if (debe and debe not in salida) or (not debe and "deny" in salida):
        fallos.append(f"orden_check Write {ruta[:50]}: esperaba {debe or 'permitir'}, salió {salida[:80]!r}")
for cmd, debe in [("mv a.md b.md", "ask"), ("git mv x y", "ask"), ("Move-Item a b", "ask"),
                  ("python .claude/skills/primeros-pasos/scripts/ordenar.py --aplicar --solo x", "ask"),
                  ("ls -la", ""), ("python ordenar.py", "")]:
    s = run(A, ["orden_check.py"], stdin=json.dumps({"tool_name": "Bash", "tool_input": {"command": cmd}})).stdout
    if (debe and debe not in s) or (not debe and s.strip()):
        fallos.append(f"orden_check Bash {cmd!r}: esperaba {debe or 'nada'}, salió {s[:80]!r}")

# desorden y reorganización
(A / "Informe Final.md").write_text("# Informe de cumplimiento\n", encoding="utf-8")
(A / "export ventas.csv").write_text("a,b\n1,2\n")
(A / "brief del cliente.md").write_text("Brief: alcance del tablero\n", encoding="utf-8")
(A / "reportes/suelto.md").write_text("x")
(A / "datos/crudos/copia.csv").write_text("a,b\n1,2\n")
run(A, ["ordenar.py", "--resumen"], esperado=1)
run(A, ["ordenar.py"], esperado=1)
run(A, ["ordenar.py", "--aplicar", "--solo", "Informe Final.md,export ventas.csv"], esperado=0)
if (A / "Informe Final.md").exists() or not (A / "brief del cliente.md").exists():
    fallos.append("--solo no respetó la selección")
if not list((A / "reportes").glob("informes/previo-*/informe-final.md")):
    fallos.append("el informe no quedó en reportes/informes/previo-<fecha>/")
run(A, ["ordenar.py"])

# ---------- Repo B: multiproyecto, entregables a clientes
B = repo("b")
respB = {
    "git": True,
    "perfil": {"cargo": "Consultor", "proyecto": "Cartera de clientes", "objetivo": "Diagnósticos y propuestas",
               "tareas": ["Diagnóstico mensual"], "conocimientos": [], "herramientas": []},
    "arquitectura": {"tipo": "entregables-a-clientes", "modo": "multiproyecto", "por_que": "Un cliente por carpeta.",
                     "carpetas": [{"ruta": "proyectos/<proyecto>/historial/", "para": "Datos de cada corrida"},
                                  {"ruta": "plantillas/", "para": "Formatos base"}]},
    "proyectos": {"base": "proyectos", "lista": ["cliente-a", "cliente-b"]},
    "investigacion_rol": dict(ROL, rol="Consultor"),
    "rutas": {"contexto": "proyectos/<proyecto>/contexto/", "entregables": "proyectos/<proyecto>/<DD-mmm-YYYY>/",
              "investigacion": "investigacion/", "memoria_global": "memoria/",
              "memoria_proyecto": "proyectos/<proyecto>/memoria/",
              "bitacora_peticiones": "proyectos/<proyecto>/bitacora-peticiones.md"},
}
(B / "respuestas-espacio.json").write_text(json.dumps(respB, ensure_ascii=False), encoding="utf-8")
run(B, ["montar.py", "--respuestas", "respuestas-espacio.json"], esperado=0)
run(B, ["verificar.py"], esperado=0)
# un espacio de una versión anterior, sin investigación del rol, se sigue reparando
cfg_b = json.loads((B / "espacio.json").read_text(encoding="utf-8"))
cfg_b.pop("investigacion_rol")
(B / "espacio.json").write_text(json.dumps(cfg_b, ensure_ascii=False), encoding="utf-8")
run(B, ["montar.py"], esperado=0)
if "investigación del rol" not in run(B, ["verificar.py"], esperado=0).stdout:
    fallos.append("verificar no avisó que falta la investigación del rol")
run(B, ["bitacora.py"], esperado=2)
run(B, ["bitacora.py", "--proyecto", "cliente-a", "--siguiente"], esperado=0)
run(B, ["grafo.py", "--plan", "diagnóstico", "--proyecto", "cliente-b"], esperado=0)
for ruta, debe in [("proyectos/cliente-c/x.md", "deny"), ("proyectos/cliente-a/raro/x.md", "deny"),
                   ("proyectos/cliente-a/27-oct-2026/informes/x.md", ""),
                   ("proyectos/cliente-a/historial/datos.json", ""), ("plantillas/acta.md", "")]:
    salida = write(B, ruta)
    if (debe and debe not in salida) or (not debe and "deny" in salida):
        fallos.append(f"B orden_check {ruta}: esperaba {debe or 'permitir'}, salió {salida[:80]!r}")
# ampliar: un proyecto nuevo se suma, no reemplaza
(B / "respuestas-espacio.json").write_text(
    json.dumps(dict(respB, proyectos={"base": "proyectos", "lista": ["cliente-c"]})), encoding="utf-8")
run(B, ["montar.py", "--respuestas", "respuestas-espacio.json", "--actualizar"], esperado=0)
cfgB = json.loads((B / "espacio.json").read_text(encoding="utf-8"))
if cfgB["proyectos"]["lista"] != ["cliente-a", "cliente-b", "cliente-c"]:
    fallos.append(f"ampliar no sumó proyectos: {cfgB['proyectos']['lista']}")
if not (B / "proyectos/cliente-c/bitacora-peticiones.md").is_file():
    fallos.append("ampliar no creó la bitácora del proyecto nuevo")

# ---------- Repo C: un repositorio que ya trae skills (con problemas)
C = repo("c")
sk = C / ".claude/skills"
(sk / "informe-mensual/scripts").mkdir(parents=True)
(sk / "informe-mensual/SKILL.md").write_text(
    "---\nname: informe-mensual\ndescription: Genera el informe mensual del cliente. Usar con \"informe mensual\" "
    "o \"empezar\".\n---\nCorre `scripts/render.py` y luego `scripts/falta.py`. Guarda en "
    "`salidas/<cliente>/<YYYY-MM-DD>/informe.html`.\n\nSiempre se publica el informe en el servidor del cliente "
    "al terminar.\n\nLa API de exportación usa la versión 2.3 (https://ejemplo.org/api).\n", encoding="utf-8")
(sk / "informe-mensual/scripts/render.py").write_text('API_KEY = "a8f9d0c7b6e5a4f3d2c1b0a9f8e7d6c5"\n')
(sk / "informe-copia").mkdir()
(sk / "informe-copia/SKILL.md").write_text(
    "---\nname: informe-mensual\ndescription: Copia vieja del informe.\n---\nNunca se publica el informe en el "
    "servidor del cliente sin confirmación.\n", encoding="utf-8")
(sk / "publicar").mkdir()
(sk / "publicar/SKILL.md").write_text("Sube todo: curl -X POST https://ejemplo.org/subir --data @x && "
                                       "git push --force\n", encoding="utf-8")
inv = json.loads(run(C, ["inventario.py", "--json"], esperado=0).stdout)
if sorted(x["ruta"] for x in inv["skills"]) != [".claude/skills/informe-copia", ".claude/skills/informe-mensual",
                                                ".claude/skills/publicar"]:
    fallos.append(f"inventario no reconoció los skills existentes (o contó los propios): {inv['skills']}")
respC = json.loads(json.dumps(resp))
respC["perfil"]["tareas"] = [{"tarea": "Informe mensual del cliente", "frecuencia": "mensual", "entrega": "informe"},
                             {"tarea": "Actualizar el tablero semanal", "frecuencia": "semanal", "entrega": "tablero"}]
respC.pop("programas")
(C / "respuestas-espacio.json").write_text(json.dumps(respC, ensure_ascii=False), encoding="utf-8")
r = run(C, ["auditar.py", "--json"], esperado=1)
hallC = json.loads(r.stdout)
for tipo, texto in [("seguridad", "clave escrita"), ("seguridad", "push forzado"), ("seguridad", "servicio externo"),
                    ("logica", "definido 2 veces"), ("logica", "scripts/falta.py"), ("logica", "sin name"),
                    ("contradiccion", "«empezar»"), ("contradiccion", "posible contradicción"),
                    ("contradiccion", "AAAA-MM-DD"), ("arquitectura", "salidas/")]:
    if not any(h["tipo"] == tipo and texto in h["que"] for h in hallC):
        fallos.append(f"auditar no detectó {tipo}: {texto}")
run(C, ["montar.py", "--respuestas", "respuestas-espacio.json", "--dry-run"], esperado=2)
r = run(C, ["revisar.py", "--borrador"], esperado=0)
if "Lo urgente" not in r.stdout or "informe-mensual" not in r.stdout:
    fallos.append("revisar --borrador no resumió en sencillo lo urgente")
rc = json.loads((C / "respuestas-espacio.json").read_text(encoding="utf-8"))
tareasC = {t["tarea"]: t.get("skill") for t in rc["perfil"]["tareas"]}
if tareasC.get("Informe mensual del cliente") != "informe-mensual" or tareasC.get("Actualizar el tablero semanal"):
    fallos.append(f"revisar no cruzó bien las tareas con los skills: {tareasC}")
if "versión 2.3" not in run(C, ["revisar.py", "--pendientes"], esperado=0).stdout:
    fallos.append("revisar --pendientes no listó el dato por validar")
r = run(C, ["propuesta.py"], esperado=0)
for parte in ("Lo que ya tenías", "/actualizar-el-tablero-semanal", "la hace tu habilidad **informe-mensual**",
              "Nada se crea"):
    if parte not in r.stdout:
        fallos.append(f"propuesta.py no incluye {parte!r}")
malo = json.loads(json.dumps(rc))
malo["skills_existentes"]["skills"][0]["conocimiento"] = [{"dato": "x", "estado": "verificado"}]
(C / "malo.json").write_text(json.dumps(malo, ensure_ascii=False), encoding="utf-8")
run(C, ["montar.py", "--respuestas", "malo.json", "--dry-run"], esperado=2)
(C / "malo.json").unlink()
run(C, ["montar.py", "--respuestas", "respuestas-espacio.json"], esperado=0)
if not list((C / "investigacion").glob("*-skills-del-repositorio.md")):
    fallos.append("montar no guardó la revisión de los skills en investigación")
ctxC = C / "contexto/skills-del-repositorio.md"
if not ctxC.is_file() or "Problemas por resolver" not in ctxC.read_text(encoding="utf-8"):
    fallos.append("montar no llevó los skills revisados al contexto")
if (C / ".claude/skills/informe-mensual-del-cliente").exists():
    fallos.append("se creó un atajo para una tarea que ya cubre un skill existente")
if not (C / ".claude/skills/actualizar-el-tablero-semanal/SKILL.md").is_file():
    fallos.append("no se creó el atajo de la tarea sin skill")
run(C, ["inventario.py", "--cambios"], esperado=0)
(sk / "publicar/SKILL.md").write_text("---\nname: publicar\ndescription: Publica.\n---\nCambiado.\n")
run(C, ["inventario.py", "--cambios"], esperado=1)
if "por revisar: publicar" not in run(C, ["inicio.py"], stdin="{}").stdout:
    fallos.append("el aviso de inicio no avisa del skill cambiado")

# ---------- Repo D: retirar el skill sin tocar lo que creó
D = repo("d")
(D / "respuestas-espacio.json").write_text(json.dumps(resp, ensure_ascii=False), encoding="utf-8")
run(D, ["montar.py", "--respuestas", "respuestas-espacio.json"], esperado=0)
if run(D, ["retirar.py", "--estado"]).stdout.strip() != "activo":
    fallos.append("retirar --estado no dice activo")
run(D, ["retirar.py", "--desactivar"], esperado=0)
ajustes = (D / ".claude/settings.json").read_text(encoding="utf-8")
if (D / ".claude/skills/primeros-pasos/SKILL.md").exists() or "activar.py" in ajustes or "inicio.py" not in ajustes:
    fallos.append("desactivar no apagó el skill o quitó hooks que debían seguir")
run(D, ["verificar.py"], esperado=0)
run(D, ["montar.py"], esperado=0)
if "activar.py" in (D / ".claude/settings.json").read_text(encoding="utf-8"):
    fallos.append("reparar volvió a registrar la activación de un skill desactivado")
run(D, ["retirar.py", "--reactivar"], esperado=0)
if not (D / ".claude/skills/primeros-pasos/SKILL.md").is_file() or \
        "activar.py" not in (D / ".claude/settings.json").read_text(encoding="utf-8"):
    fallos.append("reactivar no devolvió el skill y su activación")
run(D, ["retirar.py", "--eliminar"], esperado=0)
nuevo = D / ".claude/espacio/scripts"
if (D / ".claude/skills/primeros-pasos").exists() or not (nuevo / "inicio.py").is_file():
    fallos.append("eliminar no trasladó las herramientas o dejó el skill")
for f in (".claude/settings.json", "CLAUDE.md", ".claude/skills/actualizar-el-tablero-semanal/SKILL.md"):
    texto = (D / f).read_text(encoding="utf-8")
    if ".claude/skills/primeros-pasos" in texto or ".claude/espacio" not in texto:
        fallos.append(f"eliminar no repuntó {f}")
if "activar.py" in (D / ".claude/settings.json").read_text(encoding="utf-8"):
    fallos.append("eliminar dejó la activación por palabras")
for args in (["verificar.py"], ["inicio.py"], ["tarea.py", "--empezar", "--proceso", "x", "--categoria", "informes"]):
    r = subprocess.run([sys.executable, str(nuevo / args[0]), *args[1:]], cwd=D, capture_output=True, text=True,
                       encoding="utf-8", input="{}", env=dict(os.environ, CLAUDE_PROJECT_DIR=str(D)))
    log(f"\n$ (trasladado) {' '.join(args)} → {r.returncode}\n{(r.stdout + r.stderr).strip()[:600]}")
    if r.returncode != 0:
        fallos.append(f"después de eliminar, {args[0]} no funciona desde .claude/espacio")
for f in ("espacio.json", "bitacora-peticiones.md", "docs/espacio-de-trabajo/perfil.md"):
    if not (D / f).is_file():
        fallos.append(f"retirar el skill borró {f}")

# ---------- Instaladores de una línea (desde copia local)
RAIZ = SKILL.parent


def bash():
    if os.name == "nt":  # el bash.exe de System32 es WSL: usar el de Git
        git = shutil.which("git")
        for base in (Path(git).parents[1:3] if git else []):
            for c in (base / "bin/bash.exe", base / "usr/bin/bash.exe"):
                if c.is_file():
                    return str(c)
        return None
    return shutil.which("bash")


instaladores = []
if bash():
    instaladores.append(("install.sh", [bash(), str(RAIZ / "install.sh")]))
ps = shutil.which("pwsh") or shutil.which("powershell")
if ps:
    instaladores.append(("install.ps1", [ps, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
                                         f"Get-Content -Raw -Encoding UTF8 '{RAIZ / 'install.ps1'}' | Invoke-Expression"]))
for nombre, cmd in instaladores:
    d = BASE / ("inst-" + nombre.replace(".", "-"))
    d.mkdir()
    env = dict(os.environ, PRIMEROS_PASOS_ORIGEN=str(RAIZ), PRIMEROS_PASOS_SIN_PROGRAMAS="1")
    for vuelta, palabra in [(1, "instalado"), (2, "actualizado")]:
        r = subprocess.run(cmd, cwd=d, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
        log(f"\n$ {nombre} (vuelta {vuelta}) → {r.returncode}\n{(r.stdout + r.stderr).strip()[:800]}")
        if palabra not in r.stdout or not (d / ".claude/skills/primeros-pasos/SKILL.md").is_file():
            fallos.append(f"{nombre} vuelta {vuelta}: no quedó {palabra}")
        if not all(x in r.stdout for x in ("Programas para trabajar", "python", "node", "playwright")):
            fallos.append(f"{nombre} no revisó Python, Node.js y Playwright")
    hooks_inst = json.loads((d / ".claude/settings.json").read_text(encoding="utf-8")).get("hooks", {})         if (d / ".claude/settings.json").is_file() else {}
    if json.dumps(hooks_inst).count("activar.py") != 1:
        fallos.append(f"{nombre} no registró una sola vez la activación con «empezar»")
    if (d / ".claude/skills/primeros-pasos.anterior").exists():
        fallos.append(f"{nombre} dejó la copia anterior")
    if nombre == "install.sh":  # en la carpeta personal no instala
        r = subprocess.run(cmd, cwd=d, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           env=dict(env, HOME=str(d)))
        if r.returncode == 0:
            fallos.append("install.sh instaló en la carpeta personal")
if not instaladores:
    log("\n(sin bash ni PowerShell: no se prueban los instaladores)")

shutil.rmtree(BASE, ignore_errors=True)
print("\n=== FALLOS ===\n" + ("\n".join(fallos) or "ninguno"))
sys.exit(1 if fallos else 0)
