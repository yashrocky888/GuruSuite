# GuruSuite Architecture

## CRITICAL RULE: API Calculates, UI Renders

### Separation of Concerns

```
┌─────────────────────────────────────────────────────────┐
│                    guru-api                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Swiss Ephemeris (Sidereal, Lahiri)             │  │
│  │  → Planetary Positions                           │  │
│  │  → House Cusps (D1)                              │  │
│  │  → Divisional Charts (D2-D60)                    │  │
│  │  → Varga Calculations                            │  │
│  └──────────────────────────────────────────────────┘  │
│                         │                                │
│                         │ JSON                            │
│                         ▼                                │
└─────────────────────────────────────────────────────────┘
                         │
                         │
┌─────────────────────────────────────────────────────────┐
│                    guru-web                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Render JSON                                     │  │
│  │  → Place planets in house boxes                  │  │
│  │  → Display sign glyphs                           │  │
│  │  → Show degrees                                  │  │
│  │  NO CALCULATIONS                                 │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## API Contract (LOCKED)

### Request
```json
{
  "dob": "1995-05-16",
  "time": "18:38",
  "lat": 12.9716,
  "lon": 77.5946,
  "timezone": "Asia/Kolkata"
}
```

### Response
```json
{
  "chart": {
    "d1": {
      "ascendant": {
        "longitude": 212.2667,
        "sign": "Vrishchika",
        "sign_index": 7,
        "house": 1,
        "degrees_in_sign": 2.2667
      },
      "houses": [
        {"house": 1, "sign": "Vrishchika", "cusp": 212.2667},
        {"house": 2, "sign": "Dhanu", "cusp": 242.2667},
        ...
      ],
      "planets": {
        "Sun": {
          "longitude": 31.4167,
          "sign": "Vrishabha",
          "sign_index": 1,
          "house": 7,
          "degrees_in_sign": 1.4167
        },
        ...
      }
    },
    "d9": { ... },
    "d10": { ... },
    "d12": { ... }
  },
  "meta": {
    "ayanamsa": "Lahiri",
    "zodiac": "Sidereal",
    "source": "Swiss Ephemeris",
    "julian_day": 2449845.263889
  }
}
```

## Forbidden in UI

### ❌ DO NOT:
- Calculate houses from longitudes
- Calculate signs from degrees
- Remap planets based on ascendant
- Rotate charts by lagna
- Infer house from sign
- Use house cusps for varga charts
- Reuse D1 logic for divisional charts

### ✅ DO:
- Use `planet.house` directly from API
- Use `planet.sign` directly from API
- Place planets in house boxes
- Display sign glyphs
- Show degrees as provided

## Verification

### API Tests
```bash
cd apps/guru-api
python test_d10_prokerala.py
python test_varga_assertions.py
```

### UI Tests
- No console errors about missing houses
- Planets appear in correct houses (from API)
- Signs match API response exactly

