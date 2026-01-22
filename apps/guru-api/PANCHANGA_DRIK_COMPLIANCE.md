# Panchanga Drik Panchang / Prokerala Compliance

## Status: IN PROGRESS

### ✅ COMPLETED
1. **Sunrise Calculation Fixed** (2026-01-22)
   - Changed from `BIT_DISC_CENTER | BIT_NO_REFRACTION` 
   - To `BIT_DISC_UPPER_LIMB` (includes atmospheric refraction by default)
   - Matches Drik Panchang standard

### 🔄 IN PROGRESS
2. **Exact Timestamps**
   - Current: Returns "Xh Ym" format
   - Required: Exact datetime timestamps (e.g., "02:28 AM, Jan 23")
   - Need to convert JD end times to formatted datetime strings

3. **Current + Next Values**
   - Current: Only current tithi/nakshatra/yoga
   - Required: Both current and next with exact end times
   - Implementation: Calculate at sunrise, then find next boundary

4. **Karana Array**
   - Current: Single karana object
   - Required: Array of karanas for the day (multiple can occur)
   - Implementation: Calculate all karanas from sunrise to next sunrise

### 📋 TODO
5. **Missing Fields**
   - Paksha (separate field, not just in tithi)
   - Amanta Month (lunar month name)
   - Purnimanta Month (lunar month name)
   - Moon Sign at sunrise
   - Sun Sign at sunrise
   - Shaka Samvat
   - Vikram Samvat
   - Gujarati Samvat

6. **Verification**
   - Compare outputs line-by-line with Drik Panchang website
   - Test multiple dates and locations
   - Ensure sunrise times match exactly

## Implementation Notes

### Sunrise Calculation
- ✅ Fixed to use upper limb with refraction
- Swiss Ephemeris `swe.rise_trans()` includes atmospheric refraction by default when using `BIT_DISC_UPPER_LIMB`

### Next Values Calculation
- Need to iterate JD forward until next boundary is found
- For tithi: Find when (Moon - Sun) crosses next 12° boundary
- For nakshatra: Find when Moon crosses next 13°20' boundary
- For yoga: Find when (Moon + Sun) crosses next 13°20' boundary

### Karana Array
- Each day can have 1-2 karanas
- Calculate from sunrise to next sunrise
- Return ordered array with end times

### Month Names
- Amanta: Month ending on Amavasya (new moon)
- Purnimanta: Month ending on Purnima (full moon)
- Need to determine which month based on tithi at sunrise

### Samvat Calculation
- Shaka Samvat: Current year - 78 (approximately)
- Vikram Samvat: Current year + 57 (approximately)
- Gujarati Samvat: Same as Vikram Samvat
- Need exact calculation based on date

## Testing Checklist
- [ ] Sunrise matches Drik Panchang exactly
- [ ] Sunset matches Drik Panchang exactly
- [ ] Tithi current + next match
- [ ] Nakshatra current + next match
- [ ] Yoga current + next match
- [ ] Karana array has correct entries
- [ ] All timestamps are exact (not approximate)
- [ ] Month names are correct
- [ ] Samvat years are correct
- [ ] Moon/Sun signs are correct
