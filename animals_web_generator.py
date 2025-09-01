#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import html, json, sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

PLACEHOLDER = "__REPLACE_ANIMALS_INFO__"

# ---------- helpers ----------
def read_text(p: str|Path) -> str: return Path(p).read_text(encoding="utf-8")
def write_text(p: str|Path, s: str) -> None: Path(p).write_text(s, encoding="utf-8")

def get_ci(d: Dict[str, Any], *keys: str) -> Optional[Any]:
    for k in keys:
        if k in d: return d[k]
    lm = {k.lower(): v for k, v in d.items()}
    for k in keys:
        v = lm.get(k.lower())
        if v is not None: return v
    return None

def get_field(animal: Dict[str, Any], *keys: str) -> Optional[Any]:
    v = get_ci(animal, *keys)
    if v is None:
        ch = get_ci(animal, "characteristics")
        if isinstance(ch, dict): v = get_ci(ch, *keys)
    if isinstance(v, str):
        v = v.strip()
        if not v: return None
    return v

def format_value(value: Any) -> str:
    if isinstance(value, (list, tuple)):
        value = ", ".join(str(x).strip() for x in value if str(x).strip())
    return html.escape(str(value))

def iter_animals(data: Any) -> List[Dict[str, Any]]:
    if isinstance(data, list): return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict) and isinstance(data.get("animals"), list):
        return [x for x in data["animals"] if isinstance(x, dict)]
    return []

# ---------- serialization ----------
def serialize_animal(animal: Dict[str, Any]) -> str:
    name = get_field(animal, "name")
    title_html = f'  <div class="card__title">{html.escape(str(name)).upper()}</div>\n' if name else ""

    # Einheitliche Faktenliste: zuerst die 3 Kernfelder, dann Extras
    facts: List[tuple[str, Any]] = []

    # Core
    diet = get_field(animal, "diet")
    if diet: facts.append(("Diet", diet))

    locs = get_field(animal, "locations", "location")
    first_loc = (locs[0] if isinstance(locs, list) and locs else locs) if locs else None
    if isinstance(first_loc, str) and first_loc.strip():
        facts.append(("Location", first_loc))

    typ = get_field(animal, "type")
    if typ: facts.append(("Type", typ))

    # Extras (nur wenn vorhanden)
    extras = [
        ("Lifespan", ("lifespan", "lifespan_in_wild", "lifespan_in_captivity")),
        ("Weight", ("weight", "avg_weight", "weight_range")),
        ("Length", ("length", "avg_length", "length_range")),
        ("Height", ("height", "avg_height", "height_range")),
        ("Top speed", ("top_speed", "speed", "max_speed")),
        ("Habitat", ("habitat",)),
        ("Temperament", ("temperament", "behavior")),
        ("Color(s)", ("color", "colors")),
        ("Scientific name", ("scientific_name", "latin_name")),
        ("Family", ("family",)),
        ("Order", ("order",)),
        ("Class", ("class", "class_name")),
        ("Geo range", ("geo_range", "native_region", "range")),
        ("Conservation status", ("conservation_status", "status")),
        ("Fun fact", ("fun_fact", "funfact")),
        ("Description", ("description",)),
    ]
    for label, keys in extras:
        v = get_field(animal, *keys)
        if v is not None: facts.append((label, v))

    if not (title_html or facts): return ""

    # eine einheitliche Liste rendern
    facts_html = "\n".join(
        f'    <li><span class="label">{html.escape(label)}:</span> {format_value(val)}</li>'
        for label, val in facts
    )

    item = '  <li class="cards__item">\n'
    if title_html: item += title_html
    item += '  <ul class="card__facts">\n' + facts_html + "\n  </ul>\n"
    item += "  </li>\n"
    return item

def build_cards(animals: Iterable[Dict[str, Any]]) -> str:
    return "".join(serialize_animal(a) for a in animals if isinstance(a, dict))

# ---------- main ----------
def main() -> None:
    json_path     = sys.argv[1] if len(sys.argv) > 1 else "animals_data.json"
    template_path = sys.argv[2] if len(sys.argv) > 2 else "animals_template.html"
    out_path      = sys.argv[3] if len(sys.argv) > 3 else "animals.html"

    try:
        template_html = read_text(template_path)
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Read error: {e}"); sys.exit(1)

    final_html = template_html.replace(PLACEHOLDER, build_cards(iter_animals(data)))
    try:
        write_text(out_path, final_html)
    except Exception as e:
        print(f"❌ Write error: {e}"); sys.exit(1)
    print(f"✅ Wrote {out_path}")

if __name__ == "__main__":
    main()
