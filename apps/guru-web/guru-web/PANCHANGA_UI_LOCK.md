# PANCHANGA UI LOCK — RENDER ONLY

**STATUS**: FROZEN / RENDER-ONLY  
**DATE**: 2026-01-22  
**RULE**: Frontend NEVER calculates Panchanga

---

## 🔒 ABSOLUTE RULE

**Frontend = Mirror of Backend**

- ✅ Render data from API
- ❌ NO calculations
- ❌ NO inference
- ❌ NO fallbacks
- ❌ NO astrology logic

**If data is missing → Backend bug (not UI fix)**

---

## 📋 UI REQUIREMENTS

### 1. Layout

- ✅ **TABLE LAYOUT ONLY**
- ❌ NO cards
- ❌ NO card-based UI
- ✅ Clean, structured table

### 2. Data Display

**Required Fields:**
- Sunrise / Sunset
- Vara (weekday + lord)
- Tithi (current + next with "upto" times)
- Nakshatra (current + next with "upto" times)
- Yoga (current + next with "upto" times)
- Karana (ordered array with "upto" times)
- Paksha
- Amanta Month
- Purnimanta Month
- Adhika Masa flag (if true)
- Moon Sign
- Sun Sign
- Samvat (Shaka, Vikram, Gujarati)

**Display Rules:**
- Show "upto" for end times
- Show "next" for next values
- Render all Karanas in order
- Use "—" for missing values (not "N/A")
- Conditional rendering (only show if present)

### 3. Routing

- `/panchanga` → Main Panchanga table page
- `/panchang` → Redirect to `/panchanga`

---

## 🚫 PROHIBITED ACTIONS

**Frontend MUST NEVER:**

1. Calculate sunrise/sunset
2. Calculate tithi/nakshatra/yoga/karana
3. Infer missing values
4. Apply fallback logic
5. Modify API response data
6. Add astrology interpretation
7. Use AI for calculations

---

## ✅ CORRECT PATTERN

```typescript
// ✅ CORRECT: Render-only
const { panchanga } = apiResponse;
return (
  <table>
    <tr>
      <td>Sunrise</td>
      <td>{panchanga.sunrise ?? "—"}</td>
    </tr>
    <tr>
      <td>Tithi</td>
      <td>
        {panchanga.tithi?.current?.name ?? "—"}
        {panchanga.tithi?.current?.end_time && (
          <span> upto {panchanga.tithi.current.end_time}</span>
        )}
      </td>
    </tr>
  </table>
);
```

```typescript
// ❌ WRONG: Calculation in frontend
const tithi = calculateTithi(moon, sun); // NO!
const sunrise = estimateSunrise(lat, lon); // NO!
```

---

## 🐛 ERROR HANDLING

**If data is missing:**

1. **DO**: Show "—" (dash)
2. **DO**: Log error to console
3. **DO**: Report as backend bug
4. **DON'T**: Calculate missing value
5. **DON'T**: Use fallback logic
6. **DON'T**: Guess or infer

---

## 📍 FILE LOCATIONS

- **Main Page**: `app/panchanga/page.tsx`
- **API Service**: `services/api.ts`
- **Old Cards** (deprecated): `components/PanchangCards.tsx`

---

## 🔐 FREEZE STATUS

**Panchanga UI Status**: **FROZEN**

- ✅ Render-only implementation
- ✅ No calculations
- ✅ No inference
- ✅ Trusts backend as single source of truth

**Last Updated**: 2026-01-22

---

**END OF UI LOCK DOCUMENT**
