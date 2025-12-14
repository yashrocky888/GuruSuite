# GURU Web Application Documentation

## Overview

GURU is a premium web application for Vedic astrology insights, predictions, and spiritual guidance. The application consumes the GURU API (Phases 1-21) backend.

## Project Structure

```
guru-web/
├── app/                    # Next.js App Router pages
├── frontend/
│   ├── components/         # React components
│   ├── layouts/            # Layout components
│   ├── pages/              # Page components (legacy, using app/ now)
│   ├── styles/             # Additional styles
│   ├── hooks/              # Custom React hooks
│   ├── utils/              # Utility functions
│   ├── state/              # Zustand state stores
│   ├── services/           # API service layer
│   ├── assets/             # Static assets
│   └── animations/         # Framer Motion animations
├── guru-personality/       # Guru personality engine
│   ├── prompt-templates/   # AI prompt templates
│   ├── conversation-engine/# Chat orchestration
│   ├── memory/             # User memory management
│   └── formatters/         # Response formatting
├── tests/                  # Test files
├── config/                 # Configuration files
└── docs/                   # Documentation
```

## Technology Stack

- **Framework**: Next.js 16 (App Router)
- **Styling**: TailwindCSS v4
- **Animations**: Framer Motion
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Icons**: Heroicons & Lucide React
- **Charts**: Recharts
- **Language**: TypeScript

## UI/UX Principles

1. **Super Clean Design**: Apple-style minimalism
2. **Soft Gradients**: Blue-purple, gold-white spiritual tones
3. **Smooth Animations**: Framer Motion throughout
4. **Glassmorphism**: Optional blur & depth effects
5. **Spiritual Vibe**: Golden aura, Sanskrit-inspired typography
6. **Mobile-First**: Responsive design from mobile to desktop

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Run development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000)

## API Integration

The application is designed to consume the GURU API backend. Update the API base URL in:
- `config/api.config.ts`
- `frontend/services/guruApi.ts`

## Next Steps

- Connect API endpoints
- Implement Guru Chat interface
- Build Kundali chart visualization
- Add prediction components
- Implement user authentication

