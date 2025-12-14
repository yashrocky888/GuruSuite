# Testing the GURU Frontend

## Quick Start

### 1. Start Backend (Terminal 1)
```bash
cd ../guru-api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 2. Start Frontend (Terminal 2)
```bash
cd guru-web
npm install
npm run dev
```

### 3. Open Browser
Navigate to: **http://localhost:3000**

---

## Test Each Page

### ✅ Home Page (`/`)
1. Enter birth details
2. Click "Generate Chart"
3. Should redirect to dashboard

### ✅ Dashboard (`/dashboard`)
- View overview
- Click quick links to other pages

### ✅ Kundli (`/kundli`)
- View birth chart
- Check planet table
- Click "Divisional Charts"

### ✅ Divisional Charts (`/kundli/divisional`)
- Select different charts (D1-D12)
- Verify chart updates

### ✅ Dasha (`/dasha`)
- View planetary periods timeline

### ✅ Transits (`/transits`)
- View transit wheel
- Check transit table

### ✅ Panchang (`/panchang`)
- View panchang cards
- Check timings

### ✅ Guru (`/guru`)
- Enter question
- Click "Get Guru's Reading"
- Wait for AI response

---

## Check Browser Console

Press **F12** and check:
- No red errors
- API calls in Network tab
- State updates in React DevTools

---

## Troubleshooting

**Backend not running?**
```bash
cd ../guru-api
uvicorn main:app --reload
```

**Frontend not starting?**
```bash
npm install
npm run dev
```

**API errors?**
- Check backend is on port 8000
- Check CORS settings
- Verify `.env` file has API key

---

## Expected Behavior

✅ All pages load
✅ Forms work
✅ Navigation smooth
✅ API calls succeed (or show errors gracefully)
✅ UI looks polished
✅ Animations smooth

