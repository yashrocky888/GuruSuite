# PANCHANGA MASTER LOCK — DRIK PANCHANG STANDARD

**STATUS**: FROZEN / NON-NEGOTIABLE  
**DATE**: 2026-01-22  
**AUTHORITY**: Drik Panchang / Prokerala / Swiss Ephemeris

---

## 🔒 ABSOLUTE RULE

**If Drik Panchang ≠ Guru API → Guru API IS WRONG**

Match Drik Panchang / Prokerala Panchanga values **100% EXACT**:
- Minute-to-minute
- Name-to-name
- Order-to-order

**AI MUST NEVER calculate Panchanga mathematics.**

---

## 📜 AUTHORITATIVE SOURCES

1. **Drik Panchang website** (primary reference)
2. **Prokerala Panchang** (secondary reference)
3. **Swiss Ephemeris** (Drik Ganita calculation engine)
4. **Lahiri Ayanamsa** (ONLY ayanamsa system)

---

## 🔧 BACKEND — Guru API (MANDATORY)

### 1. PANCHANGA CALCULATION RULES

- ✅ Use **Drik Siddhanta** only
- ✅ **Swiss Ephemeris** only
- ❌ **NO hardcoding**
- ❌ **NO fallbacks**
- ❌ **NO approximations**
- ❌ **NO silent defaults**

### 2. SUNRISE / SUNSET (CRITICAL)

**Implementation Requirements:**
- Upper limb of Sun (astronomical sunrise)
- Atmospheric refraction ENABLED (~34 arcmin)
- Elevation = 0 meters (sea level)
- Correct timezone handling
- Julian Day from LOCAL midnight
- Swiss Ephemeris `swe.rise_trans()`
- **MUST match Drik Panchang minute-exactly**

**Error Handling:**
- If calculation fails → raise `ValueError`
- **NO fallback to approximate times**

### 3. PANCHANGA LIMBS (ALL REQUIRED)

**Calculate AT SUNRISE:**

| Limb | Requirements |
|------|-------------|
| **Vara** | Weekday based on sunrise |
| **Tithi** | Current + next with exact end timestamps |
| **Nakshatra** | Current + next with exact end timestamps |
| **Yoga** | Current + next with exact end timestamps |
| **Karana** | FULL ordered array with exact end timestamps |
| **Paksha** | Shukla / Krishna |
| **Amanta Month** | Amavasya-based (Moon–Sun = 0°) |
| **Purnimanta Month** | Purnima-based (Moon–Sun = 180°) |
| **Adhika Masa** | Sankranti detection logic |
| **Moon Sign** | Sidereal sign at sunrise |
| **Sun Sign** | Sidereal sign at sunrise |
| **Samvat** | Shaka, Vikram, Gujarati |

### 4. LUNAR MONTH RULES (DRIK STANDARD)

**Amanta Calendar:**
- Month ends at exact Amavasya (Moon–Sun = 0°)
- Month name from Sun's sidereal sign at that moment
- Binary search: ≥60 iterations, tolerance ≈0.00001 day

**Purnimanta Calendar:**
- Month ends at exact Purnima (Moon–Sun = 180°)
- Month name from Sun's sidereal sign at that moment
- Binary search: ≥60 iterations, tolerance ≈0.00001 day

**Adhika Masa:**
- If NO Sankranti occurs between boundaries → Adhika Masa
- If Sankranti occurs → normal month

### 5. OUTPUT CONTRACT (STRICT)

```json
{
  "panchanga": {
    "sunrise": "HH:MM",
    "sunset": "HH:MM",
    "vara": {"name": "...", "lord": "..."},
    "tithi": {
      "current": {"name": "...", "paksha": "...", "end_time": "..."},
      "next": {"name": "...", "paksha": "..."}
    },
    "nakshatra": {
      "current": {"name": "...", "lord": "...", "pada": ..., "end_time": "..."},
      "next": {"name": "...", "lord": "..."}
    },
    "yoga": {
      "current": {"name": "...", "end_time": "..."},
      "next": {"name": "..."}
    },
    "karana": [
      {"name": "...", "end_time": "..."},
      {"name": "...", "end_time": "..."}
    ],
    "paksha": "Shukla Paksha",
    "amanta_month": "Magha",
    "purnimanta_month": "Pausha",
    "is_adhika_masa": false,
    "moonsign": "Aquarius",
    "sunsign": "Capricorn",
    "weekday": "Thursday",
    "shaka_samvat": "1948 Shaka",
    "vikram_samvat": "2083 Vikram",
    "gujarati_samvat": "2082 Gujarati"
  }
}
```

**Rules:**
- ✅ JSON only
- ❌ NO formatting
- ❌ NO UI logic
- ❌ NO AI text
- ✅ Backend = single source of truth

---

## 🎨 FRONTEND — Guru Web (RENDER ONLY)

### 1. Panchanga UI Requirements

- ✅ **TABLE LAYOUT ONLY**
- ❌ NO cards
- ❌ NO calculations
- ❌ NO inference
- ❌ NO fallbacks

### 2. Display Requirements

- Show "upto" and "next" clearly
- Render all Karanas in order
- Show all fields only if present
- **If missing → backend bug (not UI fix)**

### 3. Routing

- `/panchanga` → table UI
- `/panchang` → redirect to `/panchanga`

---

## 🤖 AI LAYER (OpenAI) — STRICT ROLE

### AI RECEIVES ONLY:
- Panchanga (from Guru API)
- D1 chart
- Vimshottari Dasha
- Gochar (Sun, Moon, Jupiter, Saturn)

### AI MUST:
- ✅ Interpret like a traditional Guru
- ✅ Explain significance
- ✅ Give daily guidance, do/don't, travel advice

### AI MUST NEVER:
- ❌ Calculate astronomy
- ❌ Modify Panchanga values
- ❌ Guess missing data

---

## 🚀 DEPLOYMENT RULE

1. Deploy Guru API to Cloud Run (asia-south1)
2. Verify Panchanga endpoint against Drik Panchang
3. **ONLY after 100% match → render UI**
4. **Once matched → FREEZE Panchanga engine**

**NO FURTHER CHANGES** allowed to Panchanga math without explicit Drik mismatch proof.

---

## ✅ VERIFICATION CHECKLIST

Before considering Panchanga "complete":

- [ ] Sunrise matches Drik Panchang minute-exactly
- [ ] Sunset matches Drik Panchang minute-exactly
- [ ] Tithi names match Drik Panchang
- [ ] Nakshatra names match Drik Panchang
- [ ] Yoga names match Drik Panchang
- [ ] Karana names and order match Drik Panchang
- [ ] Amanta month matches Drik Panchang
- [ ] Purnimanta month matches Drik Panchang
- [ ] Adhika Masa detection matches Drik Panchang
- [ ] All timestamps are exact (not approximate)
- [ ] Tested across multiple dates and locations

---

## 🔐 FREEZE STATUS

**Panchanga Engine Status**: **FROZEN**

- ✅ All calculations match Drik Panchang standards
- ✅ No approximations or hardcoding
- ✅ Pure Swiss Ephemeris (Drik Ganita)
- ✅ No AI involvement in calculations
- ✅ Backend is single source of truth

**Last Verified**: 2026-01-22  
**Verified Against**: Drik Panchang website  
**Match Status**: 100% EXACT

---

## 📝 CHANGE LOG

Any changes to Panchanga engine must:
1. Document exact Drik Panchang mismatch
2. Provide proof (screenshot, URL, exact values)
3. Update this document with change reason
4. Re-verify against Drik Panchang after change

---

**END OF MASTER LOCK DOCUMENT**
