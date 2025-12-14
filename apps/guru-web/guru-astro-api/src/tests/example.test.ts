/**
 * Example Test - Validate calculation flow
 */

import { calculateAstroChart } from '../services/astroService';

describe('Astrology Calculations', () => {
  it('should calculate chart for May 16, 1995, 6:38 PM, Bangalore', async () => {
    const birthData = {
      name: 'Test User',
      date: '16/05/1995',
      time: '06:38 PM',
      city: 'bangalore',
      country: 'india',
    };

    const result = await calculateAstroChart(birthData, 'lahiri', 'placidus');

    expect(result).toBeDefined();
    expect(result.planets).toHaveLength(9);
    expect(result.lagna).toBeDefined();
    expect(result.rashiChartNorth).toBeDefined();
    expect(result.rashiChartSouth).toBeDefined();
  });
});

