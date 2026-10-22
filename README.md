# 한길 (Hangil) data

Indoor map and street-view photos for Hangil, kept apart from code so the survey team can update them without touching the backend.

| Path | What |
| --- | --- |
| `maps/<map_id>.json` | Floors, nodes, passages (`edges`), destinations (`pois`), signs (`landmarks`), panoramas. Loaded by the backend at start-up |
| `panos/` | 360° photos (WebP, long side 2560 px). Served at `/panos/<file>` on the demo site |
| `schema/map.schema.json` | JSON Schema of a map file, generated from the backend's `MapData` model |
| `tools/validate.py` | Schema, reference and photo-file checks; runs on every push |

## What is real

`maps/seoul-station.json`: only the floors of the AREX ticket points (express B2, all-stop B3) and platforms (B7) are confirmed, from the [AREX official guide](https://www.airportrailroad.com/co/steUsfGud.do) on 2026-10-22. Positions, passages, distances, headings and sign texts are placeholders until the field survey.

The photos in `panos/` are **CC0 samples of other stations** from [Poly Haven](https://polyhaven.com) (Hamburg Hbf, a subway passage, Amsterdam Noord and Vijzelgracht); every panorama using them has `"is_example": true`. Replace them with the Seoul Station shoot, and **blur faces before committing**: this repo is public.

## Editing a map

1. Edit `maps/seoul-station.json` and bump `version` (e.g. `2026-10-22.1` → `2026-10-29.1`). Clients holding the old version get `409 MAP_VERSION_MISMATCH` and reload.
2. A panorama's arrow is `north_yaw_deg + edge heading_deg`: record where north sits in each photo, and the compass bearing of each passage (north = 0°, clockwise).
3. Check locally, then push:

   ```sh
   pip install "jsonschema>=4.23,<5" && python tools/validate.py
   ```

4. Deploy: run the backend workflow (`gh workflow run ci.yml -R team-onetruck/oneload-backend`). It validates this repo again against the backend model before switching the server over.

When the backend's map model changes, regenerate the schema from a backend checkout:

```sh
uv run python -c "import json; from app.domain.mapdata import MapData; print(json.dumps(MapData.model_json_schema(), ensure_ascii=False, indent=2))" > ../oneload-data/schema/map.schema.json
```
