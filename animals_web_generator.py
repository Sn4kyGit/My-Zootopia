#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
import html
from typing import Any, Dict, List, Optional

PLACEHOLDER = "__REPLACE_ANIMALS_INFO__"

def get_ci(d: Dict[str, Any], *keys: str) -> Optional[Any]:
    """Case-insensitive Getter für mögliche Feldnamen."""
    for k in keys:
        if k in d:
            return d[k]
    lower_map = {k.lower(): v for k, v in d.items()}
    for k in keys:
        v = lower_map.get(k.lower())
        if v is not None:
            return v
    return None

def iter_animals(data: Any) -> List[Dict[str, Any]]:
    """Akzeptiert eine List[dict] oder ein Dict mit Schlüssel 'animals'."""
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict) and isinstance(data.get("animals"), list):
        return [x for x in data["animals"] if isinstance(x, dict)]
    return []

def read_template(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def main() -> None:
    # Pfade: JSON (Arg1, optional), Template (Arg2, optional), Output (Arg3, optional)
    json_path = sys.argv[1] if len(sys.argv) > 1 else "animals_data.json"
    template_path = sys.argv[2] if len(sys.argv) > 2 else "animals_template.html"
    out_path = sys.argv[3] if len(sys.argv) > 3 else "animals.html"

    # (1) Template lesen
    template_html = read_template(template_path)

    # JSON laden
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    animals = iter_animals(data)

    # (2) HTML-String mit <li class="cards__item">-Blöcken bauen
    output = ""
    for a in animals:
        lines = []

        # Name
        name = get_ci(a, "name")
        if name:
            lines.append(f"Name: {html.escape(str(name))}<br/>")

        # Diet (top-level oder unter characteristics)
        diet = get_ci(a, "diet")
        if not diet:
            ch = get_ci(a, "characteristics")
            if isinstance(ch, dict):
                diet = get_ci(ch, "diet")
        if diet:
            lines.append(f"Diet: {html.escape(str(diet))}<br/>")

        # Location (erste aus Liste oder String)
        locations = get_ci(a, "locations", "location")
        first_location = None
        if isinstance(locations, list) and locations:
            first_location = locations[0]
        elif isinstance(locations, str) and locations.strip():
            first_location = locations.strip()
        if first_location:
            lines.append(f"Location: {html.escape(str(first_location))}<br/>")

        # Type (top-level oder unter characteristics)
        typ = get_ci(a, "type")
        if not typ:
            ch = get_ci(a, "characteristics")
            if isinstance(ch, dict):
                typ = get_ci(ch, "type")
        if typ:
            lines.append(f"Type: {html.escape(str(typ))}<br/>")

        # Nur wenn es mindestens eine Zeile gibt, ein <li> schreiben
        if lines:
            output += '    <li class="cards__item">\n'
            output += '    ' + "\n    ".join(lines) + "\n"
            output += '    </li>\n'

    # (3) Platzhalter im Template ersetzen
    final_html = template_html.replace(PLACEHOLDER, output)

    # (4) In neue Datei schreiben
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(final_html)

    print(f"✅ {out_path} geschrieben ({len(animals)} Tiere verarbeitet).")

if __name__ == "__main__":
    main()
