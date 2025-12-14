# GURU Project Testing Guide

## Quick Start Testing

### 1. Start the Backend API Server

```bash
# Navigate to backend directory
cd guru-api

# Install Python dependencies (if not already done)
pip install -r requirements.txt

# Start the FastAPI server
uvicorn main:app --reload --port 8000
```

The backend will be available at: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

### 2. Start the Frontend Development Server

```bash
# Navigate to frontend directory
cd guru-web

# Install dependencies (if not already done)
npm install

# Start the Next.js dev server
npm run dev
```

The frontend will be available at: `http://localhost:3000`

---

## Testing Each Page

### 1. Home Page (`/`)
**What to test:**
- ✅ Form displays correctly
- ✅ Can enter birth details (date, time, place)
- ✅ Form validation works
- ✅ Submit button redirects to dashboard

**Test Steps:**
1. Open `http://localhost:3000`
2. Fill in birth details:
   - Date: Any valid date
   - Time: Any valid time (e.g., 10:30)
   - Place: Any city name
   - Coordinates: Optional (can be 0, 0)
3. Click "Generate Chart"
4. Should redirect to `/dashboard`

---

### 2. Dashboard (`/dashboard`)
**What to test:**
- ✅ Dashboard loads
- ✅ Shows birth details if available
- ✅ Quick links to other pages work
- ✅ Overview data displays (if API connected)

**Test Steps:**
1. Navigate to `http://localhost:3000/dashboard`
2. Check if birth details are shown
3. Click each quick link card:
   - Kundli Chart
   - Dasha Timeline
   - Transits
   - Panchang

---

### 3. Kundli Chart (`/kundli`)
**What to test:**
- ✅ Chart visualization renders
- ✅ Planet positions display
- ✅ Data table shows planet data
- ✅ Link to divisional charts works

**Test Steps:**
1. Navigate to `http://localhost:3000/kundli`
2. Check if chart canvas renders
3. Verify planet table displays
4. Click "Divisional Charts" link

**Note:** If no data, check browser console for API errors.

---

### 4. Divisional Charts (`/kundli/divisional`)
**What to test:**
- ✅ Chart selector buttons work
- ✅ Different charts load when selected
- ✅ Chart info displays correctly

**Test Steps:**
1. Navigate to `http://localhost:3000/kundli/divisional`
2. Click different chart buttons (D1, D2, D3, etc.)
3. Verify chart updates for each selection

---

### 5. Dasha Timeline (`/dasha`)
**What to test:**
- ✅ Timeline component renders
- ✅ Periods display correctly
- ✅ Dates and durations show

**Test Steps:**
1. Navigate to `http://localhost:3000/dasha`
2. Check if timeline displays
3. Verify period information is shown

---

### 6. Transits (`/transits`)
**What to test:**
- ✅ Transit wheel renders
- ✅ Transit table displays
- ✅ Planet positions show correctly

**Test Steps:**
1. Navigate to `http://localhost:3000/transits`
2. Check transit wheel visualization
3. Verify transit table data

---

### 7. Panchang (`/panchang`)
**What to test:**
- ✅ Panchang cards display
- ✅ Tithi, Nakshatra, Yoga, Karana show
- ✅ Timings display correctly

**Test Steps:**
1. Navigate to `http://localhost:3000/panchang`
2. Check all 4 main cards (Tithi, Nakshatra, Yoga, Karana)
3. Verify timings section

---

### 8. Guru Page (`/guru`) - AI Interpretation
**What to test:**
- ✅ Question input field works
- ✅ "Get Guru's Reading" button works
- ✅ API call to backend succeeds
- ✅ AI response displays
- ✅ Error handling works

**Test Steps:**
1. Navigate to `http://localhost:3000/guru`
2. Enter a question (e.g., "What does my chart say about my career?")
3. Click "Get Guru's Reading"
4. Wait for AI response
5. Verify response displays in the reading box

**Important:** This requires the backend API to be running and the AI endpoint to be functional.

---

## Testing API Connections

### Check Backend Health

```bash
# Test backend health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","api_key_loaded":true,"api_key_preview":"XhsJ59EZ5v..."}
```

### Test API Endpoints

```bash
# Test chat endpoint (Guru AI)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What does my chart say?",
    "context": "You are a Vedic astrology guru."
  }'

# Test birth details endpoint
curl -X POST http://localhost:8000/api/birth-details \
  -H "Content-Type: application/json" \
  -d '{
    "date": "1990-01-01",
    "time": "10:30",
    "place": "Mumbai",
    "latitude": 19.0760,
    "longitude": 72.8777
  }'
```

---

## Browser Testing Checklist

### Visual Testing
- [ ] All pages load without errors
- [ ] Glassmorphic UI effects display correctly
- [ ] Animations work smoothly
- [ ] Responsive design works on mobile/tablet/desktop
- [ ] Colors and gradients display properly

### Functional Testing
- [ ] Navigation between pages works
- [ ] Forms submit correctly
- [ ] API calls succeed (check Network tab)
- [ ] Loading states display
- [ ] Error messages show when API fails
- [ ] State persists (birth details saved)

### Browser Console
Open DevTools (F12) and check:
- [ ] No JavaScript errors
- [ ] No API 404 errors (unless backend not running)
- [ ] Network requests succeed
- [ ] No CORS errors

---

## Common Issues & Solutions

### Issue: "Failed to fetch" errors
**Solution:** 
- Ensure backend is running on port 8000
- Check CORS settings in backend
- Verify API_BASE_URL in `services/api.ts`

### Issue: API key not loaded
**Solution:**
- Check `.env` file exists in project root
- Verify `GURU_API_KEY` is set
- Restart backend server after adding .env

### Issue: Pages show "No data available"
**Solution:**
- This is normal if backend endpoints aren't fully implemented
- Check browser console for API errors
- Verify backend endpoints match frontend calls

### Issue: Build errors
**Solution:**
```bash
# Clean and rebuild
cd guru-web
rm -rf .next node_modules
npm install
npm run build
```

---

## Testing with Mock Data

If backend isn't fully ready, you can test UI with mock data:

1. **Temporarily modify API calls** in `services/api.ts` to return mock data
2. **Use browser DevTools** to mock API responses
3. **Test components in isolation** by passing mock props

---

## Performance Testing

```bash
# Build for production
cd guru-web
npm run build

# Test production build
npm start

# Check bundle size
npm run build
# Check .next/analyze for bundle analysis
```

---

## Automated Testing (Future)

Consider adding:
- Unit tests for components (Jest + React Testing Library)
- Integration tests for API calls
- E2E tests (Playwright/Cypress)

---

## Quick Test Commands

```bash
# Start everything (in separate terminals)
# Terminal 1: Backend
cd guru-api && uvicorn main:app --reload

# Terminal 2: Frontend
cd guru-web && npm run dev

# Terminal 3: Test API
curl http://localhost:8000/health
```

---

## Success Indicators

✅ All pages load without errors
✅ Navigation works smoothly
✅ Forms submit and redirect correctly
✅ API calls return data (or show proper errors)
✅ UI looks polished with glassmorphic effects
✅ Animations are smooth
✅ Mobile responsive design works

---

## Next Steps After Testing

1. Connect real backend endpoints
2. Add error boundaries
3. Implement loading skeletons
4. Add form validation
5. Optimize performance
6. Add analytics

