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

// Global error handler middleware (must be after routes)
app.use((err: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
  // If response already sent, delegate to default handler
  if (res.headersSent) {
    return next(err);
  }
  
  const statusCode = err.status || err.statusCode || 500;
  const errorResponse = err.response || err;
  
  // Log error in development
  if (process.env.NODE_ENV === 'development') {
    console.error('Unhandled error:', {
      path: req.path,
      method: req.method,
      status: statusCode,
      message: err.message,
      stack: err.stack
    });
  }
  
  res.status(statusCode).json({
    success: false,
    status: statusCode,
    error: {
      message: err.message || errorResponse?.error?.message || 'Internal server error',
      type: errorResponse?.error?.type || err.name || 'ServerError',
      source: 'guru-astro-api'
    }
  });
});

// 404 handler
app.use((req: express.Request, res: express.Response) => {
  res.status(404).json({
    success: false,
    status: 404,
    error: {
      message: `Route not found: ${req.method} ${req.path}`,
      type: 'NotFoundError',
      source: 'guru-astro-api'
    }
  });
});

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

