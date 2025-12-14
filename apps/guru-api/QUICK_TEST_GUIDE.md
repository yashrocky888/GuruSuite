# Quick Test Guide - Phase 6 Yogas Engine

## 🚀 Fastest Way to Test

### Option 1: Run Test Script (Easiest)

```bash
cd /Users/yashm/Guru_API
python3 test_yogas_quick.py
```

This will test all yoga endpoints automatically!

### Option 2: Test in Browser (Visual)

1. **Start the server** (if not running):
   ```bash
   cd /Users/yashm/Guru_API
   uvicorn src.main:app --reload
   ```

2. **Open browser**:
   ```
   http://localhost:8000/docs
   ```

3. **Find "Yogas" section** and click on `/yogas/all`

4. **Click "Try it out"**

5. **Enter test data**:
   - `dob`: `1995-05-16`
   - `time`: `18:38`
   - `lat`: `12.97`
   - `lon`: `77.59`

6. **Click "Execute"**

### Option 3: Use curl (Command Line)

```bash
# Test all yogas
curl "http://localhost:8000/yogas/all?dob=1995-05-16&time=18:38&lat=12.97&lon=77.59"

# Test major yogas only
curl "http://localhost:8000/yogas/major?dob=1995-05-16&time=18:38&lat=12.97&lon=77.59"

# Test planetary yogas
curl "http://localhost:8000/yogas/planetary?dob=1995-05-16&time=18:38&lat=12.97&lon=77.59"

# Test house yogas
curl "http://localhost:8000/yogas/house?dob=1995-05-16&time=18:38&lat=12.97&lon=77.59"
```

### Option 4: Direct Python Test (No Server Needed)

```bash
cd /Users/yashm/Guru_API
python3 << 'EOF'
from src.jyotish.yogas.yoga_engine import detect_all_yogas
from src.jyotish.kundli_engine import generate_kundli
from src.utils.converters import degrees_to_sign
import swisseph as swe

# Test data
jd = swe.julday(1995, 5, 16, 18 + 38/60.0, swe.GREG_CAL)
k = generate_kundli(jd, 12.97, 77.59)

# Prepare planets
planets = {}
for p, d in k['Planets'].items():
    if p in ["Rahu", "Ketu"]:
        continue
    sign_num, _ = degrees_to_sign(d['degree'])
    asc_deg = k['Ascendant']['degree']
    rel_pos = (d['degree'] - asc_deg) % 360
    house_num = int(rel_pos / 30) + 1
    if house_num > 12:
        house_num = 1
    planets[p] = {'degree': d['degree'], 'sign': sign_num, 'house': house_num}

# Prepare houses
houses = []
asc_sign, _ = degrees_to_sign(k['Ascendant']['degree'])
houses.append({'house': 1, 'degree': k['Ascendant']['degree'], 'sign': asc_sign})
for h in k['Houses']:
    sign_num, _ = degrees_to_sign(h['degree'])
    houses.append({'house': h['house'], 'degree': h['degree'], 'sign': sign_num})

# Detect yogas
yogas = detect_all_yogas(planets, houses)

print("✅ YOGAS DETECTED:")
print(f"Total: {yogas['total_yogas']}")
print(f"Major: {len(yogas['major_yogas'])}")
print(f"Moderate: {len(yogas['moderate_yogas'])}")
print(f"Doshas: {len(yogas['doshas'])}")
print("\nSample Yogas:")
for yoga in yogas['all_yogas'][:10]:
    print(f"  - {yoga['name']} ({yoga['category']})")
EOF
```

## 📋 Expected Results

You should see:
- **Total Yogas**: 25-27
- **Major Yogas**: 1-2
- **Moderate Yogas**: 21-23
- **Doshas**: 3

## 🔧 Troubleshooting

### Server Not Running?
```bash
cd /Users/yashm/Guru_API
uvicorn src.main:app --reload
```

### Connection Error?
- Make sure server is running on port 8000
- Check: `curl http://localhost:8000/health`

### Timeout Error?
- Server may be slow on first request
- Try again after a few seconds
- Or use direct Python test (Option 4)

## ✅ Quick Verification

Run this to verify everything works:

```bash
cd /Users/yashm/Guru_API
python3 test_yogas_quick.py
```

If you see "✅ Success!" messages, everything is working! 🎉

