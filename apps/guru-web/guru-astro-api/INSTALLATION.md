# Installation Guide - Guru Astrology API

## Prerequisites

- Node.js 18+ 
- npm or yarn

## Installation Steps

### 1. Install Dependencies

```bash
cd guru-astro-api
npm install
```

### 2. Swiss Ephemeris Setup

**Important**: The Swiss Ephemeris library requires additional setup:

#### Option A: Use sweph npm package (if available)
```bash
npm install sweph
```

#### Option B: Use Python swisseph with Node.js wrapper
If `sweph` package is not available, you may need to:
1. Install Python swisseph: `pip install pyswisseph`
2. Use a Node.js wrapper or fallback to simplified calculations

#### Option C: Use Fallback Mode
The code includes fallback calculations that work without Swiss Ephemeris, but with reduced accuracy.

### 3. Build

```bash
npm run build
```

### 4. Run

**Development:**
```bash
npm run dev
```

**Production:**
```bash
npm start
```

## Testing

```bash
npm test
```

## API Endpoints

Once running, the API will be available at:
- `http://localhost:3001/api/astro/calculate`
- `http://localhost:3001/api/astro/chart`
- `http://localhost:3001/api/astro/divisional`

## Example Request

```bash
curl -X POST http://localhost:3001/api/astro/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "dob": "16/05/1995",
    "tob": "06:38 PM",
    "city": "bangalore",
    "country": "india",
    "system": "lahiri",
    "houseSystem": "placidus"
  }'
```

## Notes

- The code includes fallback calculations if Swiss Ephemeris is not available
- For production, Swiss Ephemeris is highly recommended for accuracy
- Timezone handling uses `moment-timezone`
- Geolocation uses a simplified city database (extend as needed)

