/**
 * Guru Astrology API - Phase 2
 * Main Express server
 */

import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import astroRoutes from './api/routes';
import locationRoutes from './api/locationRoutes';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'guru-astro-api' });
});

// API routes
app.use('/api/astro', astroRoutes);
app.use('/api/location', locationRoutes);

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Guru Astrology API running on port ${PORT}`);
  console.log(`📊 Endpoints:`);
  console.log(`   POST /api/astro/calculate`);
  console.log(`   POST /api/astro/chart`);
  console.log(`   POST /api/astro/divisional`);
  console.log(`   GET  /api/location/search?q=query`);
  console.log(`   GET  /api/location/coordinates?city=...&country=...`);
});

