#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
from typing import Any, Dict, List, Optional

PLACEHOLDER = "__REPLACE_ANIMALS_INFO__"

def get_ci(d: Dict[str, Any], *keys: str) -> Optional[Any]:
    # Case-insensitive Getter
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
    # akzeptiert Liste oder { "animals": [...] }
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict) and isinstance(data.get("animals"), list):
        return [x for x in data["animals"] if isinstance(x, dict)]
    return []

def read_template(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def main() -> None:
    # Pfade: JSON (Arg 1, optional), Template (Arg 2, optional), Output (Arg 3, optional)
    json_path = sys.argv[1] if len(sys.argv) > 1 else "animals_data.json"
    template_path = sys.argv[2] if len(sys.argv) > 2 else "animals_template.html"
    out_path = sys.argv[3] if len(sys.argv) > 3 else "animals.html"

    # (1) Template lesen
    template_html = read_template(template_path)

    # JSON laden
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    animals = iter_animals(data)

    # (2) String mit Tierdaten bauen
    output = ""
    for a in animals:
        any_field = False

        name = get_ci(a, "name")
        if name:
            output += f"Name: {name}\n"
            any_field = True

        diet = get_ci(a, "diet")
        if not diet:
            ch = get_ci(a, "characteristics")
            if isinstance(ch, dict):
                diet = get_ci(ch, "diet")
        if diet:
            output += f"Diet: {diet}\n"
            any_field = True

        locations = get_ci(a, "locations", "location")
        first_location = None
        if isinstance(locations, list) and locations:
            first_location = locations[0]
        elif isinstance(locations, str) and locations.strip():
            first_location = locations.strip()
        if first_location:
            output += f"Location: {first_location}\n"
            any_field = True

        typ = get_ci(a, "type")
        if not typ:
            ch = get_ci(a, "characteristics")
            if isinstance(ch, dict):
                typ = get_ci(ch, "type")
        if typ:
            output += f"Type: {typ}\n"
            any_field = True

        if any_field:
            output += "\n"  # Leerzeile zwischen den Tieren

    # (3) Platzhalter ersetzen
    final_html = template_html.replace(PLACEHOLDER, output)

    # (4) In neue Datei schreiben
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(final_html)

    print(f"✅ {out_path} geschrieben ({len(animals)} Tiere verarbeitet).")

if __name__ == "__main__":
    main()
