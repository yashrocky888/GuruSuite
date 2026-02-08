# SHADBALA GO-LIVE — FINAL DEPLOYMENT

## ✅ PRE-DEPLOYMENT VERIFICATION (COMPLETE)

### Backend Code ✅
- SHADBALA_CONFIG: PURE BPHS (1.0 / 1.0 / 1.0) ✅
- Status function: `calculate_bphs_status()` ✅
- API response: Includes `status` and `ratio` ✅
- Code status: READY

### Frontend Code ✅
- Build status: ✅ Successfully built
- Shadbala page: `/shadbala` route generated ✅
- Status badges: Implemented ✅
- Tooltips: Implemented ✅
- Transparency note: Implemented ✅
- Code status: READY

---

## 🚀 DEPLOYMENT STEPS

### STEP 1: BACKEND RESTART

**Production API (Cloud Run):**
```bash
# Deploy to Cloud Run (if using gcloud)
cd apps/guru-api
gcloud run deploy guru-api \
  --source . \
  --region asia-south1 \
  --platform managed
```

**OR if using Docker:**
```bash
cd apps/guru-api
docker-compose restart guru-api
```

**OR if direct Python:**
```bash
cd apps/guru-api
pkill -f "uvicorn.*main:app"
python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

**Verify Backend:**
```bash
curl "https://guru-api-660206747784.asia-south1.run.app/strength/shadbala?dob=2006-02-03&time=22:30&lat=12.9716&lon=77.5946" \
  | jq '.shadbala.Sun.status'
```

**Expected:** Status string ("Very Strong", "Strong", "Average", or "Weak")

---

### STEP 2: FRONTEND DEPLOYMENT

**Build is complete:** ✅ `.next/` directory exists

**Deploy to Vercel:**
```bash
cd apps/guru-web/guru-web
vercel --prod
```

**OR deploy using your hosting service:**
- The build output is in `.next/` directory
- Deploy according to your hosting platform's instructions

**Frontend URL:** (Your Vercel/hosting URL)
- Expected: `https://your-domain.vercel.app/shadbala` or similar

---

### STEP 3: CACHE CLEARING

**CDN Cache:**
- Clear Vercel CDN cache (if using Vercel)
- Clear Cloudflare cache (if using Cloudflare)
- Clear any other CDN cache

**Browser Cache:**
- Hard refresh: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)
- Or clear browser cache manually

**Service Worker:**
- Disable service worker if present
- Or update service worker cache version

---

### STEP 4: LIVE VERIFICATION

**API Test:**
```bash
curl "https://guru-api-660206747784.asia-south1.run.app/strength/shadbala?dob=2006-02-03&time=22:30&lat=12.9716&lon=77.5946" \
  | jq '.shadbala.Sun | {total_shadbala, shadbala_in_rupas, relative_rank, ratio, status}'
```

**UI Verification Checklist:**
- [ ] Navigate to `/shadbala` page
- [ ] Page loads without error
- [ ] "Calculation Mode: PURE BPHS (No heuristics)" visible
- [ ] All 7 planets rendered
- [ ] Each planet shows:
    - Total Virupas (large, bold)
    - Rupas
    - Rank
    - Status badge (color + label)
- [ ] Tooltip appears on hover/touch for each Bala
- [ ] Transparency note visible at bottom
- [ ] No NaN / Infinity values
- [ ] Dig Bala values ∈ [0, 60]
- [ ] Ranks are unique (1–7)

---

## 🔗 EXPECTED URLS

**Backend API:**
- Production: `https://guru-api-660206747784.asia-south1.run.app`
- Shadbala Endpoint: `https://guru-api-660206747784.asia-south1.run.app/strength/shadbala`

**Frontend:**
- (Your Vercel/hosting URL)
- Shadbala Page: `https://your-domain.vercel.app/shadbala`

---

## ✅ FINAL STATUS

**Backend:** Code ready, restart required
**Frontend:** Built successfully, deployment required
**Configuration:** PURE BPHS (1.0 / 1.0 / 1.0)
**Status Logic:** BPHS-derived thresholds
**UI:** Render-only, no client-side logic

---

## 📝 POST-DEPLOYMENT

After deployment, run:
```bash
bash SHADBALA_GO_LIVE_VERIFICATION.sh
```

This will verify:
- API returns status and ratio fields
- API returns PURE BPHS calculation_mode
- Status values are valid

---

**Ready for Go-Live! 🚀**
