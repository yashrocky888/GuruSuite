# Guru Astrology Core Engine - Phase 2

Complete Vedic Astrology calculation engine using Swiss Ephemeris.

## Features

- ✅ Birth Data Engine (validation, timezone, DST, geolocation)
- ✅ Swiss Ephemeris Integration (sidereal Lahiri)
- ✅ Planetary Position Calculator (Sun → Ketu)
- ✅ House Calculation (Placidus + Whole Sign)
- ✅ Rashi Chart Generator (North + South Indian)
- ✅ Nakshatra Calculation
- ✅ Divisional Charts (D1, D9 Navamsa)

## Installation

```bash
cd guru-astro-api
npm install
```

## Development

```bash
npm run dev
```

## Build

```bash
npm run build
npm start
```

## API Endpoints

### POST /api/astro/calculate

Calculate complete astrological chart.

**Request:**
```json
{
  "name": "John Doe",
  "dob": "16/05/1995",
  "tob": "06:38 PM",
  "city": "bangalore",
  "country": "india",
  "system": "lahiri",
  "houseSystem": "placidus"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "birthData": { ... },
    "planets": [ ... ],
    "houses": [ ... ],
    "lagna": { ... },
    "rashiChartNorth": { ... },
    "rashiChartSouth": { ... },
    "navamsaChart": { ... }
  }
}
```

### POST /api/astro/chart

Get rashi chart only.

### POST /api/astro/divisional?type=D9

Get divisional charts (D1 or D9).

## Project Structure

```
guru-astro-api/
├── src/
│   ├── astro-core/
│   │   ├── birthdata/      # Birth data parsing & validation
│   │   ├── ephemeris/      # Swiss Ephemeris integration
│   │   ├── calculators/    # Planet, house, nakshatra calculators
│   │   ├── charts/        # Chart generators
│   │   └── utils/         # Constants & utilities
│   ├── api/               # Express routes
│   ├── services/          # Business logic
│   └── types/             # TypeScript types
└── dist/                  # Compiled output
```

## Dependencies

- `swisseph` - Swiss Ephemeris library
- `moment-timezone` - Timezone handling
- `express` - Web server
- `typescript` - Type safety

