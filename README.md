# GuruSuite - Vedic Astrology Monorepo

## Architecture

**CRITICAL RULE**: API calculates, UI only renders.

### Structure

```
GuruSuite/
├── apps/
│   ├── guru-api/      # ALL astro calculations (Swiss Ephemeris, JHora-compatible)
│   └── guru-web/      # UI rendering ONLY (no calculations)
├── README.md
└── .gitignore
```

## Absolute Rules

### RULE 1: API is Single Source of Truth
- ALL planetary positions calculated ONLY in `guru-api`
- Swiss Ephemeris (sidereal, Lahiri ayanamsa)
- JHora/Drik Panchang compatible

### RULE 2: UI is Dumb Renderer
- `guru-web` MUST NEVER:
  - Compute signs
  - Compute houses
  - Compute divisional placements
  - Remap planets
- UI ONLY renders JSON from API

### RULE 3: Divisional Charts
- Calculated ONLY using longitude slicing
- NO sign-based shortcuts
- NO reusing D1 houses
- Match Prokerala/JHora exactly

## API Contract

```json
{
  "chart": {
    "d1": { "ascendant": {}, "houses": [], "planets": [] },
    "d9": { "ascendant": {}, "houses": [], "planets": [] },
    "d10": { "ascendant": {}, "houses": [], "planets": [] }
  },
  "meta": {
    "ayanamsa": "Lahiri",
    "zodiac": "Sidereal",
    "source": "Swiss Ephemeris"
  }
}
```

## Development

### API
```bash
cd apps/guru-api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload
```

### Web
```bash
cd apps/guru-web
npm install
npm run dev
```

## Verification

Run tests:
```bash
cd apps/guru-api
python test_d10_prokerala.py
python test_varga_assertions.py
```

