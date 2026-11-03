import ast
from pathlib import Path


_SOURCE_FILE = Path(__file__).resolve().parent.parent / "trabajoF.py"
_CLASS_NAMES = {
    "NodoSimple",
    "ListaSimple",
    "NodoDoble",
    "ListaDoble",
    "NodoCola",
    "ColaSimple",
    "NodoPila",
    "Pila",
}
_source = _SOURCE_FILE.read_text(encoding="utf-8")
_tree = ast.parse(_source, filename=str(_SOURCE_FILE))
_class_nodes = [
    node
    for node in _tree.body
    if isinstance(node, ast.ClassDef) and node.name in _CLASS_NAMES
]
_found_names = {node.name for node in _class_nodes}
_missing_names = _CLASS_NAMES - _found_names
if _missing_names:
    raise RuntimeError(
        f"No se encontraron estas clases en {_SOURCE_FILE.name}: "
        f"{', '.join(sorted(_missing_names))}"
    )

_class_module = ast.Module(body=_class_nodes, type_ignores=[])
exec(compile(_class_module, str(_SOURCE_FILE), "exec"), globals())

alumnos_db = ListaSimple()
temas_db = ListaDoble()
dudas_cola = ColaSimple()
historial_pila = Pila()
