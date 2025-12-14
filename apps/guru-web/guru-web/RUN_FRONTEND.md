# How to Run the GURU Frontend

## Quick Start

### 1. Navigate to the frontend directory
```bash
cd guru-web
```

### 2. Install dependencies (first time only)
```bash
npm install
```

### 3. Run the development server
```bash
npm run dev
```

## Frontend will run on:
- **URL**: http://localhost:3000
- **Auto-reload**: Enabled (changes refresh automatically)

## Prerequisites

### Backend must be running
The frontend connects to the backend API at `http://localhost:8000/api/v1`

Make sure the backend is running:
```bash
# In another terminal
cd guru-api
python3 main.py
```

## Available Scripts

### Development
```bash
npm run dev
```
Starts Next.js development server with hot-reload on port 3000

### Production Build
```bash
npm run build
npm start
```
Builds and starts production server

### Lint
```bash
npm run lint
```
Runs ESLint to check code quality

## Environment Variables

The frontend uses:
- `NEXT_PUBLIC_API_URL` - Backend API URL (defaults to `http://localhost:8000/api/v1`)

To change the API URL, create a `.env.local` file:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Troubleshooting

### Port 3000 already in use
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or run on different port
PORT=3001 npm run dev
```

### Module not found errors
```bash
# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Backend connection errors
- Verify backend is running: `curl http://localhost:8000/health`
- Check API URL in `services/api.ts`
- Ensure CORS is enabled in backend

### Build errors
```bash
# Clear Next.js cache
rm -rf .next
npm run build
```

## Project Structure

```
guru-web/
├── app/              # Next.js App Router pages
├── components/       # React components
├── services/         # API service layer
├── store/            # Zustand state management
├── styles/           # Global styles
└── public/           # Static assets
```

## Development Tips

1. **Hot Reload**: Changes to files automatically refresh the browser
2. **TypeScript**: Full TypeScript support - check for type errors
3. **Tailwind CSS**: Utility-first CSS framework
4. **State Management**: Zustand stores in `store/` directory
5. **API Calls**: All API calls go through `services/api.ts`

## Common Workflow

1. Start backend (Terminal 1):
   ```bash
   cd guru-api
   python3 main.py
   ```

2. Start frontend (Terminal 2):
   ```bash
   cd guru-web
   npm run dev
   ```

3. Open browser:
   ```
   http://localhost:3000
   ```

## Pages Available

- `/` - Birth details input
- `/dashboard` - Dashboard
- `/kundli` - Main kundli chart
- `/kundli/divisional` - Divisional charts (D9, D10)
- `/dasha` - Dasha timeline
- `/transits` - Transit information
- `/panchang` - Panchang data
- `/guru` - AI Guru readings
- And more...

