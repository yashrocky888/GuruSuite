# Swiss Ephemeris Data Files Setup

## Status
✅ Code updated to automatically detect ephemeris file paths
⚠️  Ephemeris data files (seplm*.se1) need to be downloaded

## Quick Setup

### Option 1: Download from Official Source (Recommended)
1. Visit: https://www.astro.com/swisseph/swephinfo_e.htm
2. Download the Swiss Ephemeris data files
3. Extract to: `apps/guru-api/ephe/`
4. Required files: `seplm*.se1` (planetary ephemeris files)

### Option 2: Install via Package Manager

**macOS:**
```bash
brew install swisseph
# Files will be in /usr/local/share/swisseph/
```

**Linux (Debian/Ubuntu):**
```bash
sudo apt-get install swisseph-data
# Files will be in /usr/share/swisseph/
```

**Linux (RedHat/CentOS):**
```bash
sudo yum install swisseph-data
# Files will be in /usr/share/swisseph/
```

### Option 3: Manual Download Script
```bash
cd apps/guru-api
mkdir -p ephe
cd ephe
# Download seplm48.se1 from https://www.astro.com/swisseph/swephinfo_e.htm
# Or use wget/curl if direct links are available
```

## Verification

Run the setup script to check:
```bash
python3 setup_ephemeris.py
```

Or test directly:
```bash
python3 -c "import swisseph as swe; swe.set_ephe_path('ephe'); result = swe.calc_ut(2453770.0, swe.SUN, swe.FLG_SWIEPH); print('SUCCESS' if result[0] == 0 else 'FAILED - files needed')"
```

## Code Changes Made

1. **`src/jyotish/strength/shadbala.py`**: 
   - Added automatic ephemeris path detection
   - Checks multiple system and local paths
   - Falls back gracefully if files not found

2. **`test_shadbala_bphs_structural.py`**:
   - Added error handling for missing ephemeris files
   - Provides clear instructions when files are missing

## Once Files Are Available

All test scripts will run automatically:
- `test_shadbala_bphs_structural.py` - BPHS structural verification
- `test_shadbala_smoke.py` - Smoke tests
- `test_shadbala_jhora_validation.py` - JHora cross-validation

The code will automatically detect and use the ephemeris files once they're in place.
