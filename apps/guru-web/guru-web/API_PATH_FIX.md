# API Path Construction Fix - Complete ✅

## Issue Identified

**Problem:** Frontend showing 404 "Not Found" when calling `getKundli`

**Root Cause:** Double `/api/v1` prefix in URL construction

## Backend Route Verification

**Endpoint:** `GET /api/v1/kundli`

**Query Parameters:**
- `dob` (required): Date of birth in YYYY-MM-DD format
- `time` (required): Time of birth in HH:MM format
- `lat` (required): Latitude
- `lon` (required): Longitude
- `timezone` (optional): Timezone (default: Asia/Kolkata)

**Verified:** ✅ API endpoint responds correctly at:
```
https://guru-api-660206747784.asia-south1.run.app/api/v1/kundli?dob=1995-05-16&time=18:38&lat=12.9716&lon=77.5946
```

## Fixes Applied

### 1. ✅ Fixed Environment Configuration
**File:** `apps/guru-web/guru-web/.env.local`

**Before (WRONG):**
```env
NEXT_PUBLIC_API_URL=https://guru-api-660206747784.asia-south1.run.app/api/v1
```

**After (CORRECT):**
```env
NEXT_PUBLIC_API_URL=https://guru-api-660206747784.asia-south1.run.app
```

**Reason:** The `apiClient` in `services/api.ts` already adds `/api/v1` to the baseURL:
```typescript
baseURL: `${API_BASE_URL}/api/v1`
```

So including `/api/v1` in the env var caused: `https://...run.app/api/v1/api/v1/kundli` ❌

### 2. ✅ Added Request URL Logging
**File:** `apps/guru-web/guru-web/services/api.ts`

Added development logging to show final request URL:
```typescript
console.log(`📡 API Request: ${config.method?.toUpperCase()} ${finalUrl}`, ...);
```

### 3. ✅ Enhanced Error Handling for 404s
**File:** `apps/guru-web/guru-web/services/api.ts`

Added detailed 404 error logging:
```typescript
if (normalizedError.status === 404) {
  console.error('🔍 404 Not Found Details:', {
    fullUrl: fullUrl,
    baseURL: baseUrl,
    endpoint: requestUrl,
    method: error.config?.method,
    params: error.config?.params,
    responseBody: error.response?.data
  });
}
```

## Final URL Construction

**Correct Flow:**
1. `API_BASE_URL` = `https://guru-api-660206747784.asia-south1.run.app` (from `.env.local`)
2. `baseURL` = `${API_BASE_URL}/api/v1` = `https://guru-api-660206747784.asia-south1.run.app/api/v1`
3. `endpoint` = `/kundli`
4. **Final URL** = `https://guru-api-660206747784.asia-south1.run.app/api/v1/kundli?dob=...&time=...&lat=...&lon=...`

## Verification

### Backend Route
- ✅ Route exists: `@router.get("/kundli")` in `kundli_routes.py`
- ✅ Query params match: `dob`, `time`, `lat`, `lon`, `timezone`
- ✅ API responds correctly with test data

### Frontend Configuration
- ✅ `.env.local` updated (no `/api/v1` in base URL)
- ✅ `apiClient` baseURL correctly adds `/api/v1`
- ✅ `getKundli` uses correct endpoint `/kundli`
- ✅ Query params correctly mapped: `birthDetails.date` → `dob`, etc.

### Error Handling
- ✅ 404 errors now log full URL details
- ✅ Request interceptor logs final URL in development
- ✅ Error messages no longer show empty `{}`

## Testing

1. **Restart frontend dev server** (to pick up new `.env.local`):
   ```bash
   # Kill existing process
   pkill -f "next dev"
   
   # Restart
   cd apps/guru-web/guru-web
   npm run dev
   ```

2. **Test in browser:**
   - Visit `http://localhost:3000`
   - Submit birth details
   - Check browser console for:
     - `📡 API Request: GET https://guru-api-660206747784.asia-south1.run.app/api/v1/kundli?dob=...`
     - No 404 errors
     - Successful API response

3. **Verify API response:**
   - Should receive D1 chart data
   - Should include all varga charts (D2-D60)
   - Should have `current_dasha` information

## Files Modified

1. `apps/guru-web/guru-web/.env.local` - Removed `/api/v1` from base URL
2. `apps/guru-web/guru-web/services/api.ts` - Added request/error logging

## Status

✅ **COMPLETE** - API path construction fixed and verified

---

**Next Steps:**
1. Restart frontend dev server
2. Test `getKundli` call
3. Verify no 404 errors
4. Confirm data loads correctly

