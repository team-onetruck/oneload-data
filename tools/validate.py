"""Checks every map before it can reach the server: JSON schema, references between items, and that each
panorama file exists. Run from the repo root: python tools/validate.py"""

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent


def problems(map_file: Path, validator: Draft202012Validator) -> list[str]:
    data = json.loads(map_file.read_text())
    found = [f"schema: {'/'.join(map(str, e.path))}: {e.message}" for e in validator.iter_errors(data)]
    if found:
        return found  # references are meaningless on a structurally broken file

    nodes = {n["id"] for n in data["nodes"]}
    floors = {f["floor_id"] for f in data["floors"]}
    refs = [
        *((f"node {n['id']} floor", n["floor_id"], floors) for n in data["nodes"]),
        *((f"edge {e['from']}->{e['to']}", end, nodes) for e in data["edges"] for end in (e["from"], e["to"])),
        *((f"poi {p['poi_id']}", p["node_id"], nodes) for p in data["pois"]),
        *((f"landmark {lm['landmark_id']}", lm["node_id"], nodes) for lm in data["landmarks"]),
        *((f"panorama {p['pano_id']}", p["node_id"], nodes) for p in data["panoramas"]),
    ]
    found += [f"{owner}: unknown {ref}" for owner, ref, known in refs if ref not in known]
    # image_url is served from this repo's panos/ directory, e.g. /panos/x.webp -> panos/x.webp.
    found += [
        f"panorama {p['pano_id']}: missing file {p['image_url']}"
        for p in data["panoramas"]
        if not (ROOT / p["image_url"].lstrip("/")).is_file()
    ]
    return found


def main() -> int:
    validator = Draft202012Validator(json.loads((ROOT / "schema" / "map.schema.json").read_text()))
    failed = False
    for map_file in sorted((ROOT / "maps").glob("*.json")):
        issues = problems(map_file, validator)
        print(f"{map_file.name}: {'OK' if not issues else f'{len(issues)} problem(s)'}")
        for issue in issues:
            print(f"  - {issue}")
        failed |= bool(issues)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
