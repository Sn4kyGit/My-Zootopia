#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generate animals.html by injecting serialized animal cards into a template.

Steps:
1) Read animals_template.html
2) Load animals_data.json
3) Serialize each animal via `serialize_animal`
4) Replace placeholder and write animals.html
"""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

PLACEHOLDER = "__REPLACE_ANIMALS_INFO__"


# --------- Data helpers ---------
def get_ci(d: Dict[str, Any], *keys: str) -> Optional[Any]:
    """Case-insensitive getter: returns value for the first matching key."""
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
    """Accepts a list of animals or a dict containing key 'animals'."""
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict) and isinstance(data.get("animals"), list):
        return [x for x in data["animals"] if isinstance(x, dict)]
    return []


# --------- IO helpers ---------
def read_text(path: str | Path) -> str:
    """Read a text file as UTF-8."""
    return Path(path).read_text(encoding="utf-8")


def write_text(path: str | Path, content: str) -> None:
    """Write text to file as UTF-8."""
    Path(path).write_text(content, encoding="utf-8")


# --------- Serialization ---------
def serialize_animal(animal: Dict[str, Any]) -> str:
    """
    Serialize a single animal to the requested HTML structure:

    <li class="cards__item">
      <div class="card__title">Name</div>
      <p class="card__text">
        <strong>Diet:</strong> ...<br/>
        <strong>Location:</strong> ...<br/>
        <strong>Type:</strong> ...<br/>
      </p>
    </li>
    """
    # Title (Name)
    name = get_ci(animal, "name")
    title_html = (
        f'  <div class="card__title">{html.escape(str(name))}</div>\n'
        if name
        else ""
    )

    # Details
    details: List[str] = []

    # Diet (top-level or nested in characteristics)
    diet = get_ci(animal, "diet")
    if not diet:
        ch = get_ci(animal, "characteristics")
        if isinstance(ch, dict):
            diet = get_ci(ch, "diet")
    if diet:
        details.append(
            f'<strong>Diet:</strong> {html.escape(str(diet))}<br/>'
        )

    # Location (first from list or string)
    locations = get_ci(animal, "locations", "location")
    first_location = None
    if isinstance(locations, list) and locations:
        first_location = locations[0]
    elif isinstance(locations, str) and locations.strip():
        first_location = locations.strip()
    if first_location:
        details.append(
            f'<strong>Location:</strong> '
            f'{html.escape(str(first_location))}<br/>'
        )

    # Type (top-level or nested in characteristics)
    typ = get_ci(animal, "type")
    if not typ:
        ch = get_ci(animal, "characteristics")
        if isinstance(ch, dict):
            typ = get_ci(ch, "type")
    if typ:
        details.append(
            f'<strong>Type:</strong> {html.escape(str(typ))}<br/>'
        )

    # Build item only if we have at least a title or details
    if not (title_html or details):
        return ""

    item = '  <li class="cards__item">\n'
    if title_html:
        item += title_html
    if details:
        item += "  <p class=\"card__text\">\n"
        item += "    " + "\n    ".join(details) + "\n"
        item += "  </p>\n"
    item += "  </li>\n"
    return item


def build_cards(animals: Iterable[Dict[str, Any]]) -> str:
    """Serialize all animals and concatenate the list items."""
    return "".join(serialize_animal(a) for a in animals if isinstance(a, dict))


# --------- Main ---------
def main() -> None:
    # CLI args: json, template, out (all optional)
    json_path = sys.argv[1] if len(sys.argv) > 1 else "animals_data.json"
    template_path = (
        sys.argv[2] if len(sys.argv) > 2 else "animals_template.html"
    )
    out_path = sys.argv[3] if len(sys.argv) > 3 else "animals.html"

    # 1) Read template
    try:
        template_html = read_text(template_path)
    except OSError as e:
        print(f"Error reading template '{template_path}': {e}")
        sys.exit(1)

    # 2) Load data
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"Error reading JSON '{json_path}': {e}")
        sys.exit(1)

    animals = iter_animals(data)

    # 3) Serialize animals as card items
    cards_html = build_cards(animals)

    # 4) Replace placeholder and write output
    final_html = template_html.replace(PLACEHOLDER, cards_html)
    try:
        write_text(out_path, final_html)
    except OSError as e:
        print(f"Error writing '{out_path}': {e}")
        sys.exit(1)

    print(f"✅ Wrote {out_path} with {len(animals)} animals.")


if __name__ == "__main__":
    main()
