# Guru Astrology API - Phase 2 Project Structure

## Complete Project Tree

```
guru-astro-api/
├── src/
│   ├── astro-core/
│   │   ├── birthdata/
│   │   │   ├── parseBirthData.ts      ✅ Birth data parsing & Julian Day
│   │   │   ├── validateBirthData.ts  ✅ Input validation
│   │   │   └── geoLookup.ts          ✅ City/country to coordinates
│   │   ├── ephemeris/
│   │   │   ├── sweInit.ts            ✅ Swiss Ephemeris initialization
│   │   │   └── getPlanetPositions.ts ✅ Planet positions (sidereal)
│   │   ├── calculators/
│   │   │   ├── planetCalculator.ts   ✅ Planet info (sign, nakshatra, etc.)
│   │   │   ├── houseCalculator.ts    ✅ House calculation (Placidus/Whole Sign)
│   │   │   └── nakshatraCalculator.ts ✅ Nakshatra calculation
│   │   ├── charts/
│   │   │   ├── rashiChartNorth.ts    ✅ North Indian chart generator
│   │   │   ├── rashiChartSouth.ts    ✅ South Indian chart generator
│   │   │   └── divisional/
│   │   │       └── d9Navamsa.ts      ✅ Navamsa (D9) chart
│   │   └── utils/
│   │       └── constants.ts           ✅ Vedic constants & utilities
│   ├── api/
│   │   └── routes.ts                 ✅ Express API routes
│   ├── services/
│   │   └── astroService.ts           ✅ Main calculation orchestrator
│   ├── types/
│   │   └── index.ts                  ✅ TypeScript type definitions
│   ├── tests/
│   │   └── example.test.ts           ✅ Test examples
│   └── index.ts                      ✅ Express server entry point
├── package.json                      ✅ Dependencies & scripts
├── tsconfig.json                     ✅ TypeScript configuration
├── .gitignore                        ✅ Git ignore rules
├── README.md                         ✅ Documentation
├── PROJECT_STRUCTURE.md              ✅ This file
└── example-output.json               ✅ Sample API response
```

## Key Components

### 1. Birth Data Engine ✅
- **parseBirthData.ts**: Parses date/time, handles timezones, calculates Julian Day
- **validateBirthData.ts**: Validates all input fields
- **geoLookup.ts**: Converts city/country to coordinates

### 2. Swiss Ephemeris Integration ✅
- **sweInit.ts**: Initializes Swiss Ephemeris library
- **getPlanetPositions.ts**: Gets accurate planetary positions (sidereal Lahiri)

### 3. Calculators ✅
- **planetCalculator.ts**: Maps planets to signs, nakshatras, calculates retrograde/combust
- **houseCalculator.ts**: Calculates house cusps (Placidus & Whole Sign)
- **nakshatraCalculator.ts**: Calculates nakshatra, pada, lord

### 4. Chart Generators ✅
- **rashiChartNorth.ts**: North Indian diamond-style chart
- **rashiChartSouth.ts**: South Indian fixed-sign chart
- **d9Navamsa.ts**: Navamsa divisional chart

### 5. API Endpoints ✅
- **POST /api/astro/calculate**: Complete chart calculation
- **POST /api/astro/chart**: Rashi charts only
- **POST /api/astro/divisional**: Divisional charts (D1, D9)

## Installation & Usage

```bash
cd guru-astro-api
npm install
npm run dev  # Development
npm run build && npm start  # Production
```

## API Example

```bash
curl -X POST http://localhost:3001/api/astro/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test",
    "dob": "16/05/1995",
    "tob": "06:38 PM",
    "city": "bangalore",
    "country": "india",
    "system": "lahiri",
    "houseSystem": "placidus"
  }'
```

