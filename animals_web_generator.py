#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
from typing import Any, Dict, List, Optional

def get_ci(d: Dict[str, Any], *keys: str) -> Optional[Any]:
    """
    Case-insensitive Getter: liefert den Wert zum ersten passenden Key.
    Beispiel: get_ci(animal, "name") findet auch "Name".
    """
    # Direkter Treffer zuerst
    for k in keys:
        if k in d:
            return d[k]
    # Case-insensitive Mapping
    lower_map = {k.lower(): v for k, v in d.items()}
    for k in keys:
        v = lower_map.get(k.lower())
        if v is not None:
            return v
    return None

def iter_animals(data: Any) -> List[Dict[str, Any]]:
    """
    Akzeptiert:
    - Liste von Tieren
    - Dict mit Schlüssel "animals"
    Sonst: leere Liste.
    """
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict) and isinstance(data.get("animals"), list):
        return [x for x in data["animals"] if isinstance(x, dict)]
    return []

def main() -> None:
    path = sys.argv[1] if len(sys.argv) > 1 else "animals_data.json"

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Datei nicht gefunden: {path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Ungültiges JSON in {path}: {e}")
        sys.exit(1)

    animals = iter_animals(data)
    for animal in animals:
        printed_any = False

        name = get_ci(animal, "name")
        if name:
            print(f"Name: {name}")
            printed_any = True

        diet = get_ci(animal, "diet")
        if diet:
            print(f"Diet: {diet}")
            printed_any = True

        locations = get_ci(animal, "locations", "location")
        first_location = None
        if isinstance(locations, list) and locations:
            first_location = locations[0]
        elif isinstance(locations, str) and locations.strip():
            # Falls die Daten als String vorliegen (selten), direkt nutzen
            first_location = locations.strip()

        if first_location:
            print(f"Location: {first_location}")
            printed_any = True

        typ = get_ci(animal, "type")
        if typ:
            print(f"Type: {typ}")
            printed_any = True

        # Leere Zeile nur, wenn etwas ausgegeben wurde (wie im Beispiel)
        if printed_any:
            print()

if __name__ == "__main__":
    main()
