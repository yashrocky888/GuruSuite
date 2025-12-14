/**
 * API Routes for Astrology Calculations
 */

import { Router, Request, Response } from 'express';
import { calculateAstroChart } from '../services/astroService';
import { AstroCalculationRequest } from '../types';

const router = Router();

/**
 * POST /api/astro/calculate
 * Calculate complete astrological chart
 */
router.post('/calculate', async (req: Request, res: Response) => {
  try {
    const request: AstroCalculationRequest = req.body;
    
    // Coordinates will be automatically fetched from city/country
    // No need to pass latitude/longitude manually
    const result = await calculateAstroChart(
      {
        name: request.name,
        date: request.dob,
        time: request.tob,
        city: request.city,
        country: request.country,
        // latitude and longitude will be auto-fetched from city/country
      },
      request.system || 'lahiri',
      request.houseSystem || 'placidus'
    );

    res.json({
      success: true,
      data: result,
    });
  } catch (error: any) {
    res.status(400).json({
      success: false,
      error: error.message || 'Calculation failed',
    });
  }
});

/**
 * POST /api/astro/chart
 * Get rashi chart only
 */
router.post('/chart', async (req: Request, res: Response) => {
  try {
    const request: AstroCalculationRequest = req.body;
    
    // Coordinates will be automatically fetched from city/country
    const result = await calculateAstroChart(
      {
        name: request.name,
        date: request.dob,
        time: request.tob,
        city: request.city,
        country: request.country,
        // latitude and longitude will be auto-fetched from city/country
      },
      request.system || 'lahiri',
      request.houseSystem || 'placidus'
    );

    res.json({
      success: true,
      data: {
        rashiChartNorth: result.rashiChartNorth,
        rashiChartSouth: result.rashiChartSouth,
        lagna: result.lagna,
        planets: result.planets,
      },
    });
  } catch (error: any) {
    res.status(400).json({
      success: false,
      error: error.message || 'Chart calculation failed',
    });
  }
});

/**
 * POST /api/astro/divisional
 * Get divisional charts (D1, D9)
 */
router.post('/divisional', async (req: Request, res: Response) => {
  try {
    const request: AstroCalculationRequest = req.body;
    const chartType = req.query.type || 'D9'; // D1 or D9
    
    // Coordinates will be automatically fetched from city/country
    const result = await calculateAstroChart(
      {
        name: request.name,
        date: request.dob,
        time: request.tob,
        city: request.city,
        country: request.country,
        // latitude and longitude will be auto-fetched from city/country
      },
      request.system || 'lahiri',
      request.houseSystem || 'placidus'
    );

    if (chartType === 'D1') {
      // D1 is the main rashi chart
      res.json({
        success: true,
        data: {
          chartType: 'D1',
          rashiChartNorth: result.rashiChartNorth,
          rashiChartSouth: result.rashiChartSouth,
        },
      });
    } else {
      // D9 Navamsa
      res.json({
        success: true,
        data: result.navamsaChart,
      });
    }
  } catch (error: any) {
    res.status(400).json({
      success: false,
      error: error.message || 'Divisional chart calculation failed',
    });
  }
});

export default router;

