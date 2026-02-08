# GuruSuite Project Architecture - Complete Guide

**Version:** 2.0.0  
**Last Updated:** 2025-01-15  
**Purpose:** Comprehensive architecture documentation for AI assistants and developers

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Monorepo Structure](#monorepo-structure)
3. [Backend Architecture](#backend-architecture)
4. [Frontend Architecture](#frontend-architecture)
5. [Data Flow](#data-flow)
6. [State Management](#state-management)
7. [Chart Rendering System](#chart-rendering-system)
8. [API Contract](#api-contract)
9. [Critical Rules & Patterns](#critical-rules--patterns)
10. [Common Mistakes to Avoid](#common-mistakes-to-avoid)
11. [File Organization](#file-organization)

---

## Project Overview

GuruSuite is a **monorepo** containing two main applications:
- **`apps/guru-api`**: FastAPI backend (Python) - Calculates all astrology
- **`apps/guru-web`**: Next.js frontend (TypeScript/React) - Renders API data only

### Core Principle (NON-NEGOTIABLE)

```
┌─────────────────────────────────────────────────────────┐
│  API CALCULATES EVERYTHING → UI ONLY RENDERS           │
└─────────────────────────────────────────────────────────┘
```

**Backend (API)**: 
- ✅ Calculates planetary positions
- ✅ Calculates houses
- ✅ Calculates divisional charts (D1-D60)
- ✅ Calculates dasha, transits, predictions
- ✅ Returns complete JSON data

**Frontend (UI)**:
- ✅ Receives JSON from API
- ✅ Renders charts visually
- ✅ Displays data in UI components
- ❌ NEVER calculates astrology
- ❌ NEVER derives houses from signs
- ❌ NEVER recomputes planetary positions

---

## Monorepo Structure

```
GuruSuite/
├── apps/
│   ├── guru-api/              # Backend API (Python/FastAPI)
│   │   ├── src/
│   │   │   ├── main.py        # FastAPI app entry point
│   │   │   ├── api/           # API route handlers
│   │   │   ├── jyotish/       # Astrology calculation engine
│   │   │   ├── db/            # Database models & connection
│   │   │   └── config.py       # Settings & configuration
│   │   ├── api/               # Legacy API routes (Phase 21)
│   │   └── requirements.txt   # Python dependencies
│   │
│   └── guru-web/              # Frontend (Next.js/React/TypeScript)
│       └── guru-web/
│           ├── app/            # Next.js App Router pages
│           ├── components/    # React components
│           ├── services/      # API client (Axios)
│           ├── store/         # Zustand state management
│           └── package.json   # Node dependencies
│
├── DATABASE_CONNECTION_FIX.md    # Database fix documentation
├── README.md                      # Project overview
└── start-backend.sh / start-frontend.sh  # Startup scripts
```

---

## Backend Architecture

### Entry Point

**File**: `apps/guru-api/src/main.py`

```python
from fastapi import FastAPI
from src.api import kundli_routes, dasha_routes, ...

app = FastAPI(title="Guru API", version="2.1.0")

# Routes are registered here
app.get("/kundli")(kundli_routes.kundli_get)
app.include_router(kundli_routes.router, prefix="/api/v1", tags=["Kundli"])
```

**Start Command**:
```bash
cd apps/guru-api
uvicorn src.main:app --host 127.0.0.1 --port 8000
```

### Core Directory Structure

```
apps/guru-api/src/
├── main.py                    # FastAPI app initialization
├── config.py                  # Settings (database URL, etc.)
│
├── api/                       # API Route Handlers
│   ├── kundli_routes.py       # ⭐ MAIN: /api/v1/kundli endpoint
│   ├── dasha_routes.py        # Dasha calculations
│   ├── transit_routes.py      # Transit predictions
│   ├── panchang_routes.py     # Panchang data
│   └── ...
│
├── jyotish/                   # Astrology Calculation Engine
│   ├── varga_engine.py        # ⭐ AUTHORITATIVE: Builds all varga charts
│   ├── varga_drik.py          # Varga sign calculation formulas
│   ├── varga_houses.py        # House calculation for vargas
│   ├── kundli_calculator.py   # D1 (Rasi) chart calculation
│   └── ...
│
└── db/                        # Database Layer
    ├── database.py            # SQLAlchemy engine & session
    ├── models.py              # Database models (BirthDetail, etc.)
    └── ...
```

### Key Backend Files

#### 1. `src/api/kundli_routes.py` - Main API Endpoint

**Purpose**: Handles `/api/v1/kundli` requests, orchestrates chart generation

**Key Function**: `kundli_get(dob, time, lat, lon, timezone, user_id)`

**Flow**:
```python
1. Receive birth details (from query params OR database if user_id provided)
2. Convert to Julian Day using Swiss Ephemeris
3. Calculate D1 (Rasi) chart → base_kundli
4. Extract D1 planets and ascendant
5. For each divisional chart (D2, D3, D4, D7, D9, ...):
   - Call build_varga_chart(d1_planets, d1_ascendant, varga_number)
6. Build standardized response with all charts
7. Return JSON response
```

**Database Handling** (CRITICAL):
```python
# ✅ CORRECT: Database is optional, gracefully handled
if user_id:
    try:
        db = SessionLocal()
        birth_detail = db.query(BirthDetail).filter(...).first()
        if birth_detail:
            # Use database data
        else:
            # Fall back to query parameters
    except Exception as db_error:
        # Database unavailable → use query parameters
        print(f"⚠️  Warning: Database unavailable. Using query parameters.")
        # Continue with dob, time, lat, lon from function params
```

**Response Structure**:
```python
{
    "D1": { Ascendant, Planets, Houses },
    "D2": { Ascendant, Planets, Houses },
    "D4": { Ascendant, Planets, Houses },
    "D7": { Ascendant, Planets, Houses },
    "D9": { Ascendant, Planets, Houses },
    # ... all divisional charts
}
```

#### 2. `src/jyotish/varga_engine.py` - Chart Builder

**Purpose**: AUTHORITATIVE engine for building complete varga charts

**Key Function**: `build_varga_chart(d1_planets, d1_ascendant, varga_number)`

**What It Does**:
1. Calculates varga sign for each planet using `calculate_varga_sign()`
2. Calculates varga ascendant sign
3. Calculates houses relative to varga ascendant
4. Returns complete chart object: `{ Ascendant, Planets, Houses }`

**Critical Function**: `_normalize_sign_index(sign_index: int) -> int`
- **Location**: TOP LEVEL of file (NOT inside any function/class)
- **Purpose**: Normalizes sign indices to 0-11 range
- **Rule**: Must be defined ONCE, globally accessible

```python
# ✅ CORRECT: Top-level definition
def _normalize_sign_index(sign_index: int) -> int:
    """Normalize sign index to range 0-11."""
    if sign_index is None:
        raise ValueError("sign_index cannot be None")
    return sign_index % 12
```

#### 3. `src/jyotish/varga_drik.py` - Varga Formulas

**Purpose**: Contains pure mathematical formulas for varga sign calculation

**Key Function**: `calculate_varga_sign(longitude, varga_number)`

**D4 Formula** (Example):
```python
# D4 (Chaturthamsa): 30° / 4 = 7.5° per part
div_size = 7.5
part_index = int(math.floor(long_in_sign / div_size))
d4_sign_index = (sign_index * 4 + part_index) % 12
```

#### 4. `src/db/database.py` - Database Connection

**Purpose**: SQLAlchemy engine and session management

**Critical Configuration**:
```python
# ✅ CORRECT: Allows API to run without database
engine = create_engine(
    settings.database_url,
    pool_pre_ping=False,  # Prevents connection attempts at import time
    connect_args={"connect_timeout": 2},  # Fast timeout
    echo=settings.debug
)
```

**Why `pool_pre_ping=False`**: 
- Allows API to start even if PostgreSQL is not running
- Database operations are optional (handled in routes)

---

## Frontend Architecture

### Entry Point

**File**: `apps/guru-web/guru-web/app/layout.tsx`

**Start Command**:
```bash
cd apps/guru-web/guru-web
npm run dev
```

**Runs on**: `http://localhost:3000`

### Core Directory Structure

```
apps/guru-web/guru-web/
├── app/                        # Next.js App Router
│   ├── layout.tsx              # Root layout
│   ├── page.tsx                # Home page (birth details form)
│   ├── kundli/
│   │   ├── page.tsx            # Main kundli chart page
│   │   └── divisional/
│   │       └── page.tsx        # ⭐ Divisional charts page (D1-D60)
│   ├── dashboard/
│   │   └── page.tsx            # Dashboard with predictions
│   └── ...
│
├── components/                 # React Components
│   ├── Chart/
│   │   ├── ChartContainer.tsx  # ⭐ MAIN: Routes to chart renderers
│   │   ├── SouthIndianChart.tsx # South Indian (sign-fixed) chart
│   │   ├── NorthIndianChart.tsx  # North Indian (lagna-rotated) chart
│   │   └── ...
│   ├── BirthDetailsForm.tsx    # Birth details input form
│   └── ...
│
├── services/
│   └── api.ts                  # ⭐ Axios client for API calls
│
└── store/
    └── useBirthStore.ts        # ⭐ Zustand store (birth details persistence)
```

### Key Frontend Files

#### 1. `app/kundli/divisional/page.tsx` - Divisional Charts Page

**Purpose**: Displays all divisional charts (D1, D2, D4, D7, D9, etc.)

**Key Responsibilities**:
1. Fetch chart data from API via `getKundli()`
2. Extract chart data for selected chart type
3. Pass data to `ChartContainer` for rendering
4. Handle loading states and errors

**Data Contract (CRITICAL)**:
```typescript
// ✅ CORRECT: All charts use same format
const extractedChart = kundliResponse?.[backendChartType] ?? 
                       kundliResponse?.data?.kundli?.[backendChartType] ?? 
                       null;

// Set chartData in uniform format
setChartData({
  [backendChartType]: extractedChart  // { D1: {...}, D4: {...}, etc. }
});

// Pass to ChartContainer
<ChartContainer 
  chartData={chartData}  // { D1: {...}, D4: {...} }
  chartType={selectedChart.toUpperCase()}  // "D1", "D4", etc.
/>
```

**Zustand Integration**:
```typescript
const { birthDetails, hasHydrated } = useBirthStore();

// Wait for hydration before checking birthDetails
if (!hasHydrated) {
  return <LoadingState />;
}

if (!birthDetails) {
  return <RedirectToBirthDetails />;
}
```

#### 2. `components/Chart/ChartContainer.tsx` - Chart Router

**Purpose**: Routes chart data to appropriate renderer (South/North Indian)

**Key Responsibilities**:
1. Extract chart data: `chartData[chartType]` (e.g., `chartData.D4`)
2. Determine chart layout type (South Indian = sign-fixed, North Indian = lagna-rotated)
3. Route to `SouthIndianChart` or `NorthIndianChart`
4. Handle D4 special validation (fail loudly if missing)

**Data Extraction**:
```typescript
// ✅ CORRECT: Extract from chartData[chartType]
const apiChart = useMemo(() => {
  const chartTypeFromProp = chartType?.toUpperCase();
  
  if (chartTypeFromProp === 'D4') {
    // D4 requires strict validation
    if (!chartData?.D4) {
      console.error('❌ D4 FATAL: chartData.D4 is missing');
      return null;  // Fail loudly
    }
    return structuredClone(chartData.D4);  // Deep clone to prevent contamination
  } else {
    // Other charts
    const chartRoot = chartData?.[chartTypeFromProp];
    if (!chartRoot && chartData?.Ascendant) {
      // Fallback for legacy format
      return chartData;
    }
    return chartRoot;
  }
}, [chartData, chartType]);
```

**Chart Routing**:
```typescript
if (chartLayout === 'south-indian') {
  return <SouthIndianChart houses={houses} planets={planetsInHouse} />;
} else {
  return <NorthIndianChart houses={houses} planets={planetsInHouse} />;
}
```

#### 3. `components/Chart/SouthIndianChart.tsx` - Sign-Fixed Chart

**Purpose**: Renders South Indian chart (SIGN-FIXED layout)

**CRITICAL RULE**: 
- **Signs NEVER rotate** - Aries is always in the same box
- **Only planets move** - Based on `planet.sign` from API
- **Houses are informational** - Displayed as labels only

**Implementation**:
```typescript
// ✅ CORRECT: Fixed sign grid
const SIGN_ORDER = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
                    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'];

// Group planets by sign (from API)
const planetsBySign = planets.reduce((acc, planet) => {
  const sign = planet.sign || planet.sign_sanskrit;
  if (!acc[sign]) acc[sign] = [];
  acc[sign].push(planet);
  return acc;
}, {});

// Render: Each sign box is FIXED, planets placed by sign
{SIGN_ORDER.map(sign => (
  <div key={sign} className="sign-box">
    <div className="sign-name">{sign}</div>
    {planetsBySign[sign]?.map(planet => (
      <PlanetIcon key={planet.name} planet={planet} />
    ))}
    {ascendant.sign === sign && <AscendantMarker />}
  </div>
))}
```

**DO NOT**:
- ❌ Rotate signs based on Ascendant
- ❌ Use house numbers for planet placement
- ❌ Calculate sign positions dynamically
- ❌ Apply any Lagna-based rotation

#### 4. `components/Chart/NorthIndianChart.tsx` - Lagna-Rotated Chart

**Purpose**: Renders North Indian chart (LAGNA-ROTATED layout)

**Implementation**:
```typescript
// ✅ CORRECT: House 1 = Ascendant sign, rotate from there
const ascendantSign = houses[0]?.sign;  // House 1 sign
// Rotate houses so House 1 is at top
const rotatedHouses = rotateHouses(houses, ascendantSign);
```

#### 5. `services/api.ts` - API Client

**Purpose**: Axios client for making API requests

**Configuration**:
```typescript
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 
           'https://guru-api-660206747784.asia-south1.run.app/api/v1',
  timeout: 30000,
});
```

**Key Function**: `getKundli(birthDetails, userId?)`
```typescript
export const getKundli = async (
  birthDetails: BirthDetails,
  userId?: string
): Promise<KundliResponse> => {
  const params = {
    dob: birthDetails.date,
    time: birthDetails.time,
    lat: birthDetails.latitude,
    lon: birthDetails.longitude,
    timezone: birthDetails.timezone,
    ...(userId && { user_id: userId }),
  };
  
  const response = await api.get('/kundli', { params });
  return response.data;
};
```

#### 6. `store/useBirthStore.ts` - State Management

**Purpose**: Zustand store with persistence for birth details

**Structure**:
```typescript
interface BirthStore {
  birthDetails: BirthDetails | null;
  userId: string | null;
  lagna: number | null;
  lagnaSign: string | null;
  hasHydrated: boolean;  // ⭐ CRITICAL: SSR hydration flag
  setBirthDetails: (details: BirthDetails) => void;
  clearBirthDetails: () => void;
}

export const useBirthStore = create<BirthStore>()(
  persist(
    (set) => ({ ... }),
    {
      name: 'guru-birth-store',
      partialize: (state) => ({
        birthDetails: state.birthDetails,
        userId: state.userId,
        lagna: state.lagna,
        lagnaSign: state.lagnaSign,
      }),
      onRehydrateStorage: () => {
        return () => {
          // Set hasHydrated after rehydration completes
          useBirthStore.setState({ hasHydrated: true });
        };
      },
    }
  )
);
```

**SSR Hydration Pattern**:
```typescript
// ✅ CORRECT: Check hasHydrated before birthDetails
const { birthDetails, hasHydrated } = useBirthStore();

if (!hasHydrated) {
  return <LoadingState />;  // Same on server and client
}

if (!birthDetails) {
  return <NoBirthDetailsState />;
}
```

---

## Data Flow

### Complete Request-Response Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. USER ENTERS BIRTH DETAILS                                │
└─────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. BirthDetailsForm.tsx                                     │
│    - Collects: date, time, place, coordinates                │
│    - Stores in Zustand: useBirthStore.setBirthDetails()     │
│    - Persists to localStorage                                │
└─────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. User Navigates to /kundli/divisional                     │
└─────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. DivisionalChartsPage.tsx                                  │
│    - Checks hasHydrated (Zustand SSR)                       │
│    - Checks birthDetails exists                              │
│    - Calls getKundli(birthDetails, userId)                  │
└─────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. services/api.ts → Axios Request                          │
│    GET /api/v1/kundli?dob=...&time=...&lat=...&lon=...     │
└─────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. Backend: src/api/kundli_routes.py                        │
│    - Receives birth details                                  │
│    - (Optional) Tries database lookup if user_id provided   │
│    - Falls back to query params if DB unavailable           │
│    - Converts to Julian Day (Swiss Ephemeris)               │
└─────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────┐
│ 7. Backend: jyotish/varga_engine.py                         │
│    - Calculates D1 (Rasi) chart                             │
│    - For each varga (D2, D3, D4, D7, D9, ...):              │
│      * Calls build_varga_chart(d1_planets, d1_asc, varga)   │
│      * Calculates varga signs for all planets                │
│      * Calculates varga houses                               │
│    - Returns complete chart objects                          │
└─────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────┐
│ 8. Backend Response (JSON)                                   │
│    {                                                         │
│      "D1": { Ascendant, Planets, Houses },                  │
│      "D4": { Ascendant, Planets, Houses },                  │
│      "D9": { Ascendant, Planets, Houses },                  │
│      ...                                                     │
│    }                                                         │
└─────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────┐
│ 9. Frontend: DivisionalChartsPage.tsx                       │
│    - Receives response                                      │
│    - Extracts chart: response[selectedChart]                 │
│    - Sets state: setChartData({ [chartType]: chart })       │
└─────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────┐
│ 10. ChartContainer.tsx                                       │
│     - Extracts: chartData[chartType] (e.g., chartData.D4)   │
│     - Determines layout (South/North Indian)                │
│     - Routes to SouthIndianChart or NorthIndianChart         │
└─────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────┐
│ 11. SouthIndianChart.tsx (or NorthIndianChart.tsx)          │
│     - Renders chart visually                                 │
│     - Places planets by sign (South) or house (North)        │
│     - Displays sign glyphs, degrees, house numbers           │
└─────────────────────────────────────────────────────────────┘
```

---

## State Management

### Zustand Store Pattern

**File**: `store/useBirthStore.ts`

**Purpose**: Persist birth details across page refreshes

**Key Features**:
1. **Persistence**: Uses `persist` middleware → localStorage
2. **SSR Safe**: `hasHydrated` flag prevents hydration mismatches
3. **Partial Persistence**: Only persists necessary fields

**Usage Pattern**:
```typescript
// ✅ CORRECT: Always check hasHydrated first
const { birthDetails, hasHydrated } = useBirthStore();

useEffect(() => {
  if (typeof window !== 'undefined' && !hasHydrated) {
    useBirthStore.setState({ hasHydrated: true });
  }
}, [hasHydrated]);

if (!hasHydrated) {
  return <LoadingState />;  // Same HTML on server and client
}

if (!birthDetails) {
  return <NoDataState />;
}
```

---

## Chart Rendering System

### Chart Types

1. **D1 (Rasi)**: Main birth chart
2. **D2 (Hora)**: Wealth chart
3. **D3 (Drekkana)**: Siblings chart
4. **D4 (Chaturthamsa)**: Property chart
5. **D7 (Saptamsa)**: Children chart
6. **D9 (Navamsa)**: Marriage chart
7. **D10 (Dasamsa)**: Career chart
8. **D12 (Dwadasamsa)**: Parents chart
9. **D16 (Shodasamsa)**: Vehicles chart
10. **D20 (Vimsamsa)**: Spiritual chart
11. **D24 (Chaturvimsamsa)**: Education chart
12. **D27 (Saptavimsamsa)**: Strength chart
13. **D30 (Trimsamsa)**: Evil chart
14. **D40 (Khavedamsa)**: Auspicious chart
15. **D45 (Akshavedamsa)**: All matters chart
16. **D60 (Shashtiamsa)**: Final chart

### Layout Types

#### South Indian Chart (Sign-Fixed)
- **Rule**: Signs NEVER rotate
- **Aries always in same box**
- **Planets move by `planet.sign`**
- **Houses are informational labels**

#### North Indian Chart (Lagna-Rotated)
- **Rule**: House 1 = Ascendant sign
- **Houses rotate relative to Lagna**
- **Planets placed by `planet.house`**

---

## API Contract

### Request Format

**Endpoint**: `GET /api/v1/kundli`

**Query Parameters**:
```
dob: string          # "2006-02-03"
time: string         # "22:30"
lat: number          # 12.9767936
lon: number          # 77.590082
timezone: string     # "Asia/Kolkata"
user_id?: string     # Optional: for database lookup
```

### Response Format

```json
{
  "D1": {
    "Ascendant": {
      "sign": "Scorpio",
      "sign_index": 7,
      "sign_sanskrit": "Vrishchika",
      "degrees_in_sign": 15.5,
      "longitude": 225.5
    },
    "Planets": {
      "Sun": {
        "name": "Sun",
        "sign": "Capricorn",
        "sign_index": 9,
        "sign_sanskrit": "Makara",
        "house": 3,
        "degrees_in_sign": 20.3,
        "longitude": 290.3
      },
      "Moon": { ... },
      "Mars": { ... },
      ...
    },
    "Houses": [
      { "house": 1, "sign": "Scorpio", "sign_index": 7 },
      { "house": 2, "sign": "Sagittarius", "sign_index": 8 },
      ...
    ]
  },
  "D4": {
    "Ascendant": { ... },
    "Planets": {
      "Sun": {
        "name": "Sun",
        "sign": "Aries",
        "sign_index": 0,
        "sign_sanskrit": "Mesha",
        "house": 5,
        "degrees_in_sign": 5.2,
        "longitude": 5.2
      },
      ...
    },
    "Houses": [ ... ]
  },
  ...
}
```

### Key Naming Conventions

**Backend Returns** (snake_case):
- `sign_index` (not `signIndex`)
- `degrees_in_sign` (not `degreesInSign`)
- `sign_sanskrit` (not `signSanskrit`)

**Frontend Expects** (snake_case):
- Matches backend exactly
- No conversion needed

---

## Critical Rules & Patterns

### Rule 1: API is Single Source of Truth

**✅ DO**:
- Use `planet.sign` directly from API
- Use `planet.house` directly from API
- Use `house.sign` directly from API

**❌ DON'T**:
- Calculate signs from longitudes
- Derive houses from signs
- Recompute planetary positions
- Apply sign_index math in frontend

### Rule 2: South Indian Chart is Sign-Fixed

**✅ DO**:
- Keep sign positions FIXED
- Place planets by `planet.sign` only
- Display Ascendant as label in its sign

**❌ DON'T**:
- Rotate signs based on Ascendant
- Use house numbers for placement
- Apply Lagna-based rotation

### Rule 3: Database is Optional

**✅ DO**:
- Handle database errors gracefully
- Fall back to query parameters
- Allow API to run without PostgreSQL

**❌ DON'T**:
- Make database connection mandatory
- Crash if database unavailable
- Remove fallback logic

### Rule 4: D4 Must Fail Loudly

**✅ DO**:
- Validate D4 data structure strictly
- Return `null` if D4 missing
- Log errors clearly

**❌ DON'T**:
- Add fallbacks for D4
- Infer D4 from D1
- Silence D4 errors

### Rule 5: Zustand Hydration Pattern

**✅ DO**:
- Check `hasHydrated` before `birthDetails`
- Render same HTML on server and client
- Set `hasHydrated` after mount

**❌ DON'T**:
- Access `birthDetails` before hydration
- Use `typeof window` in render logic
- Cause hydration mismatches

---

## Common Mistakes to Avoid

### Mistake 1: Calculating Astrology in Frontend

**❌ WRONG**:
```typescript
// Frontend calculating sign from longitude
const signIndex = Math.floor(longitude / 30);
const sign = SIGNS[signIndex];
```

**✅ CORRECT**:
```typescript
// Use sign directly from API
const sign = planet.sign;  // Already calculated by backend
```

### Mistake 2: Rotating South Indian Chart

**❌ WRONG**:
```typescript
// Rotating signs based on Ascendant
const rotatedSigns = rotateArray(SIGNS, ascendant.sign_index);
```

**✅ CORRECT**:
```typescript
// Fixed sign order
const SIGN_ORDER = ['Aries', 'Taurus', ...];  // Never changes
```

### Mistake 3: Database Connection Without Error Handling

**❌ WRONG**:
```python
db = SessionLocal()  # Crashes if DB not available
birth_detail = db.query(...).first()
```

**✅ CORRECT**:
```python
try:
    db = SessionLocal()
    birth_detail = db.query(...).first()
except Exception:
    # Fall back to query parameters
    pass
```

### Mistake 4: D4 Fallback Logic

**❌ WRONG**:
```typescript
// Inferring D4 from D1
if (!chartData.D4) {
  chartData.D4 = deriveD4FromD1(chartData.D1);
}
```

**✅ CORRECT**:
```typescript
// Fail loudly if D4 missing
if (!chartData.D4) {
  console.error('❌ D4 FATAL: chartData.D4 is missing');
  return null;
}
```

### Mistake 5: Hydration Mismatch

**❌ WRONG**:
```typescript
// Different HTML on server vs client
if (typeof window !== 'undefined' && birthDetails) {
  return <Chart />;
}
return <Loading />;
```

**✅ CORRECT**:
```typescript
// Same HTML on server and client
if (!hasHydrated) {
  return <Loading />;  // Same on both
}
if (!birthDetails) {
  return <NoData />;
}
return <Chart />;
```

---

## File Organization

### Backend Files (Priority Order)

1. **`src/main.py`** - FastAPI app entry point
2. **`src/api/kundli_routes.py`** - Main kundli endpoint
3. **`src/jyotish/varga_engine.py`** - Chart builder (authoritative)
4. **`src/jyotish/varga_drik.py`** - Varga formulas
5. **`src/jyotish/varga_houses.py`** - House calculations
6. **`src/db/database.py`** - Database connection

### Frontend Files (Priority Order)

1. **`app/kundli/divisional/page.tsx`** - Divisional charts page
2. **`components/Chart/ChartContainer.tsx`** - Chart router
3. **`components/Chart/SouthIndianChart.tsx`** - Sign-fixed renderer
4. **`components/Chart/NorthIndianChart.tsx`** - Lagna-rotated renderer
5. **`services/api.ts`** - API client
6. **`store/useBirthStore.ts`** - State management

---

## Development Workflow

### Starting Backend

```bash
cd apps/guru-api
uvicorn src.main:app --host 127.0.0.1 --port 8000
```

**Verify**: `curl http://127.0.0.1:8000/health`

### Starting Frontend

```bash
cd apps/guru-web/guru-web
npm run dev
```

**Verify**: Open `http://localhost:3000`

### Testing API

```bash
curl "http://127.0.0.1:8000/api/v1/kundli?dob=2006-02-03&time=22:30&lat=12.9767936&lon=77.590082"
```

---

## Summary

**Key Takeaways**:

1. **Monorepo**: Two apps (backend + frontend)
2. **API Calculates**: All astrology in Python backend
3. **UI Renders**: Frontend only displays API data
4. **Database Optional**: Graceful fallback to query params
5. **South Indian = Sign-Fixed**: Never rotates
6. **Zustand + SSR**: Check `hasHydrated` before data
7. **D4 Strict**: Fail loudly if missing
8. **Uniform Data Contract**: `{ [chartType]: chartObject }`

**Remember**: When in doubt, check the API response. The API is the single source of truth.
