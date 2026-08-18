import { describe, it, expect } from 'vitest';
import { getRiskLevel, getAQICategory, formatTrendChange, getTrendIcon } from '../utils/risk';

describe('getRiskLevel', () => {
  it('returns LOW for score <= 20', () => { expect(getRiskLevel(10)).toBe('LOW'); });
  it('returns MODERATE for 21-40', () => { expect(getRiskLevel(30)).toBe('MODERATE'); });
  it('returns ELEVATED for 41-60', () => { expect(getRiskLevel(50)).toBe('ELEVATED'); });
  it('returns HIGH for 61-80', () => { expect(getRiskLevel(70)).toBe('HIGH'); });
  it('returns VERY HIGH for > 80', () => { expect(getRiskLevel(90)).toBe('VERY HIGH'); });
});

describe('getAQICategory', () => {
  it('returns Good for AQI <= 50', () => { expect(getAQICategory(30).label).toBe('Good'); });
  it('returns Unhealthy for AQI > 150', () => { expect(getAQICategory(180).label).toBe('Unhealthy'); });
  it('returns Hazardous for AQI > 300', () => { expect(getAQICategory(350).label).toBe('Hazardous'); });
});

describe('formatTrendChange', () => {
  it('includes + for positive', () => { expect(formatTrendChange(42)).toBe('+42%'); });
  it('no + for negative', () => { expect(formatTrendChange(-20)).toBe('-20%'); });
});

describe('getTrendIcon', () => {
  it('returns ↑ for INCREASING', () => { expect(getTrendIcon('INCREASING')).toBe('↑'); });
  it('returns ↓ for DECREASING', () => { expect(getTrendIcon('DECREASING')).toBe('↓'); });
  it('returns → for STABLE', () => { expect(getTrendIcon('STABLE')).toBe('→'); });
});
