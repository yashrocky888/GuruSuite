# Database Connection Fix - Complete Documentation

## Problem Summary

The backend API was crashing with HTTP 500 errors when trying to calculate kundli charts because it attempted to connect to a PostgreSQL database that was not running. The error occurred even when birth details were provided directly via query parameters, making the database connection unnecessary.

**Secondary Issue**: Due to the database connection errors, the API was returning HTTP 500 instead of chart data, which caused **all divisional charts (including D4) to be unavailable** in the frontend. Once the database connection issue was fixed, the D4 chart and all other divisional charts became visible again.

## Root Cause

### Error Message
```
psycopg2.OperationalError: connection to server at "localhost" (::1), port 5432 failed: Connection refused
```

### Why It Happened

1. **Backend Code Path**: When a `user_id` was provided in the API request, the backend tried to look up birth details from the database.

2. **Database Not Running**: PostgreSQL was not installed or running on the local machine (port 5432).

3. **No Error Handling**: The original code did not handle database connection failures gracefully. When `SessionLocal()` was called or when a database query was executed, it would raise an exception that propagated up and caused the entire API request to fail with HTTP 500.

4. **Unnecessary Dependency**: The API should be able to work without a database when birth details are provided directly via query parameters (`dob`, `time`, `lat`, `lon`).

## Files Modified

### 1. `apps/guru-api/src/api/kundli_routes.py`

**Location**: Lines 381-413 (database lookup section in `kundli_get` function)

**Before (Problematic Code)**:
```python
if user_id:
    db = SessionLocal()  # ❌ This would crash if DB not available
    try:
        user_id_int = int(user_id) if isinstance(user_id, str) and user_id.isdigit() else user_id
        birth_detail = db.query(BirthDetail).filter(BirthDetail.user_id == user_id_int).first()
        # ... extract birth details ...
    finally:
        db.close()
```

**After (Fixed Code)**:
```python
if user_id:
    # Try database lookup, but don't fail if DB is unavailable
    try:
        db = SessionLocal()  # ✅ Wrapped in try-except
        # Convert user_id to int if it's a string
        user_id_int = int(user_id) if isinstance(user_id, str) and user_id.isdigit() else user_id
        
        # Query birth details from database (this may fail if DB is not connected)
        try:
            birth_detail = db.query(BirthDetail).filter(BirthDetail.user_id == user_id_int).first()
            
            if birth_detail:
                # Extract birth details from database
                dob = birth_detail.birth_date.strftime("%Y-%m-%d") if birth_detail.birth_date else dob
                time = birth_detail.birth_time or time
                lat = birth_detail.birth_latitude if birth_detail.birth_latitude is not None else lat
                lon = birth_detail.birth_longitude if birth_detail.birth_longitude is not None else lon
                timezone = birth_detail.timezone or timezone
            else:
                # User not found in database - fall back to query parameters
                print(f"⚠️  Warning: user_id {user_id} not found in database. Using birth details from query parameters.")
        except Exception as query_error:
            # Query failed - fall back to query parameters
            print(f"⚠️  Warning: Database query failed ({type(query_error).__name__}). Using birth details from query parameters.")
        finally:
            try:
                db.close()
            except:
                pass
    except Exception as db_error:
        # SessionLocal() creation or connection failed - fall back to query parameters
        print(f"⚠️  Warning: Database unavailable ({type(db_error).__name__}). Using birth details from query parameters.")
        # Continue with query parameters (dob, time, lat, lon from function params)
```

**Key Changes**:
1. **Nested try-except blocks**: 
   - Outer try-except catches errors when creating `SessionLocal()` (database connection failure)
   - Inner try-except catches errors during the actual database query
   
2. **Graceful fallback**: When any database error occurs, the code prints a warning and continues using birth details from query parameters instead of crashing.

3. **Safe cleanup**: The `db.close()` is wrapped in its own try-except to prevent errors during cleanup.

### 2. `apps/guru-api/src/db/database.py`

**Location**: Lines 15-20 (database engine configuration)

**Before (Problematic Code)**:
```python
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # ❌ This tries to verify connections at import time
    echo=settings.debug
)
```

**After (Fixed Code)**:
```python
# Create database engine with lazy connection
# pool_pre_ping=False prevents connection attempts at import time
# This allows the API to run without a database
engine = create_engine(
    settings.database_url,
    pool_pre_ping=False,  # ✅ Disable pre-ping to allow running without DB
    connect_args={"connect_timeout": 2},  # Fast timeout for connection attempts
    echo=settings.debug
)
```

**Key Changes**:
1. **`pool_pre_ping=False`**: Prevents SQLAlchemy from trying to verify database connections when the engine is created. This allows the API to start even if the database is not available.

2. **`connect_timeout=2`**: Sets a fast timeout (2 seconds) for connection attempts, so if the database is unavailable, the connection attempt fails quickly rather than hanging.

## How The Fix Works

### Flow Diagram

```
API Request with user_id
    ↓
Try to create database session
    ↓
    ├─ Success → Try to query database
    │              ├─ Success → Use data from DB
    │              └─ Failure → Fall back to query params
    │
    └─ Failure (DB not available) → Fall back to query params
                                        ↓
                                    Continue with dob, time, lat, lon from request
                                        ↓
                                    Calculate kundli successfully
```

### Error Handling Strategy

1. **Layer 1 - Session Creation**: If `SessionLocal()` fails (database not running), catch the exception and continue with query parameters.

2. **Layer 2 - Database Query**: If the query itself fails (user not found, connection lost during query), catch the exception and continue with query parameters.

3. **Layer 3 - Cleanup**: If `db.close()` fails, catch the exception silently (cleanup errors are non-critical).

### Why This Works

- **Non-blocking**: Database errors no longer prevent the API from functioning
- **Backward compatible**: If the database is available and the user exists, it still uses database data
- **Forward compatible**: Works perfectly when birth details are provided directly (no database needed)
- **User-friendly**: API continues to work even in development environments without PostgreSQL

## Testing The Fix

### Test Case 1: Database Not Available
```bash
# Stop PostgreSQL (if running)
# Make API request with user_id
curl "http://127.0.0.1:8000/api/v1/kundli?user_id=123&dob=2006-02-03&time=22:30&lat=12.9767936&lon=77.590082"

# Expected: ✅ Success (uses query parameters, prints warning about DB)
```

### Test Case 2: Database Available, User Not Found
```bash
# PostgreSQL running, but user_id doesn't exist
curl "http://127.0.0.1:8000/api/v1/kundli?user_id=999&dob=2006-02-03&time=22:30&lat=12.9767936&lon=77.590082"

# Expected: ✅ Success (uses query parameters, prints warning about user not found)
```

### Test Case 3: No user_id, Only Query Parameters
```bash
# No user_id provided
curl "http://127.0.0.1:8000/api/v1/kundli?dob=2006-02-03&time=22:30&lat=12.9767936&lon=77.590082"

# Expected: ✅ Success (uses query parameters directly, no database call)
```

## Important Notes for Future Development

### DO NOT:
- ❌ Remove the try-except blocks around database operations
- ❌ Make database connection mandatory for kundli calculations
- ❌ Remove the fallback to query parameters
- ❌ Re-enable `pool_pre_ping=True` without ensuring database is always available

### DO:
- ✅ Always provide birth details as query parameters when calling the API
- ✅ Keep database operations optional and gracefully handled
- ✅ Test API functionality without a database connection
- ✅ Use the database only when it's available and user data exists

## Related Files

- **`apps/guru-api/src/api/kundli_routes.py`**: Main API route handler (modified)
- **`apps/guru-api/src/db/database.py`**: Database connection configuration (modified)
- **`apps/guru-api/src/db/models.py`**: Database models (not modified, but referenced)
- **`apps/guru-api/src/config.py`**: Application settings (not modified, but contains DATABASE_URL)

## Error Messages to Watch For

### Before Fix:
```
HTTP 500 Internal Server Error
psycopg2.OperationalError: connection to server at "localhost" (::1), port 5432 failed: Connection refused
```

### After Fix:
```
⚠️  Warning: Database unavailable (OperationalError). Using birth details from query parameters.
HTTP 200 OK (with kundli data)
```

## D4 Chart Visibility Fix

### Problem
The D4 (Chaturthamsa) chart was not visible in the frontend because:
1. **API was returning HTTP 500 errors** due to database connection failures
2. **No chart data was being returned** to the frontend
3. **Frontend showed "Chart Data Unavailable"** because the API request failed

### Solution
By fixing the database connection issue, the API now:
1. **Returns HTTP 200 with complete chart data** including all divisional charts (D1-D60)
2. **D4 chart data is included in the response** when the API call succeeds
3. **Frontend can now render D4 chart** because it receives valid data

### How D4 Chart Became Visible

**Before Fix**:
```
Frontend Request → Backend API
    ↓
Backend tries to connect to database
    ↓
Database connection fails (PostgreSQL not running)
    ↓
Backend throws exception → HTTP 500
    ↓
Frontend receives error → "Chart Data Unavailable"
    ↓
D4 chart: ❌ NOT VISIBLE
```

**After Fix**:
```
Frontend Request → Backend API
    ↓
Backend tries to connect to database
    ↓
Database connection fails → Caught by try-except
    ↓
Backend falls back to query parameters
    ↓
Backend calculates kundli successfully → HTTP 200
    ↓
Response includes: D1, D2, D3, D4, D7, D9, D10, D12, D16, D20, D24, D27, D30, D40, D45, D60
    ↓
Frontend receives valid data → Renders all charts
    ↓
D4 chart: ✅ VISIBLE
```

### Code That Enables D4 Chart

The D4 chart visibility is enabled by the same database connection fix:

**File**: `apps/guru-api/src/api/kundli_routes.py`

**Key Code Section** (Lines 381-413):
```python
if user_id:
    try:
        db = SessionLocal()
        # ... database query ...
    except Exception as db_error:
        # ✅ Database error caught - API continues instead of crashing
        print(f"⚠️  Warning: Database unavailable. Using birth details from query parameters.")
        # Continue with query parameters (dob, time, lat, lon from function params)

# ✅ API continues to calculate kundli even if database fails
# This ensures D4 and all other charts are generated and returned
jd = swe.julday(...)
base_kundli = generate_kundli(jd, lat, lon)
d4_chart = build_varga_chart(d1_planets, d1_ascendant, 4)  # ✅ D4 is calculated
# ... all other charts calculated ...
response = {
    "D1": base_kundli,
    "D4": d4_response,  # ✅ D4 included in response
    # ... all other charts ...
}
```

### Verification

**To verify D4 chart is working**:
1. Make API request: `curl "http://127.0.0.1:8000/api/v1/kundli?dob=2006-02-03&time=22:30&lat=12.9767936&lon=77.590082"`
2. Check response contains `"D4"` key with data
3. Frontend should display D4 chart when this data is received

**Expected Response Structure**:
```json
{
  "D1": { ... },
  "D4": {
    "Ascendant": { "sign": "...", "sign_index": ..., ... },
    "Planets": { "Sun": { ... }, "Moon": { ... }, ... },
    "Houses": [ ... ]
  },
  ...
}
```

## Summary

**Problem**: 
1. Backend crashed when PostgreSQL was not running, even when birth details were provided directly.
2. D4 chart (and all divisional charts) were not visible because API returned HTTP 500 errors.

**Solution**: 
1. Made database operations optional with comprehensive error handling that falls back to query parameters.
2. API now successfully calculates and returns all divisional charts (including D4) even without database.

**Result**: 
1. API works reliably with or without a database connection, making it suitable for development environments without PostgreSQL.
2. **D4 chart and all divisional charts (D1-D60) are now visible** because the API returns complete chart data successfully.
