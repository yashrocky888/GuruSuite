# Prokerala Verification Guide

## API Deployment Status
✅ **Deployed**: https://guru-api-660206747784.asia-south1.run.app

## Test Birth Data
- **Date**: 1995-05-16
- **Time**: 18:38 IST
- **Place**: Bangalore
- **Latitude**: 12.9716°N
- **Longitude**: 77.5946°E

## Verification Steps

### 1. Access Prokerala Divisional Charts
Visit: https://www.prokerala.com/astrology/divisional-charts.php

### 2. Enter Birth Details
- Name: (any)
- Gender: (any)
- Birth Date: 16 May 1995
- Birth Time: 6:38 PM (18:38)
- Place of Birth: Bangalore, Karnataka, India

### 3. Compare D10 (Dasamsa) Results

#### Expected Results (Based on User Requirements):
- **Ascendant**: Cancer (Karka)
- **Moon**: Vrishchika (Scorpio)
- **Jupiter**: Vrishchika (Scorpio)
- **Saturn**: Vrishchika (Scorpio)

#### API Endpoint for Testing:
```
GET https://guru-api-660206747784.asia-south1.run.app/api/kundli?dob=1995-05-16&time=18:38&lat=12.9716&lon=77.5946&timezone=Asia/Kolkata
```

### 4. Compare Other Varga Charts
- **D7 (Saptamsa)**: Check children/progeny chart
- **D12 (Dwadasamsa)**: Check parents chart
- **D9 (Navamsa)**: Check marriage chart

## Notes
- Prokerala uses Lahiri Ayanamsa (same as our API)
- All calculations should match within 1 arcsecond tolerance
- House assignments use Whole Sign system for varga charts

## If Mismatches Found
1. Note the specific planet and varga chart
2. Compare the sign and degrees
3. Check if it's a formula issue or house calculation issue
4. Report back with specific discrepancies

