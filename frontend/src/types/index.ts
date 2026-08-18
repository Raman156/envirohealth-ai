export type RiskLevel = 'LOW' | 'MODERATE' | 'ELEVATED' | 'HIGH' | 'VERY HIGH';
export type TrendDirection = 'INCREASING' | 'DECREASING' | 'STABLE';
export type AlertSeverity = 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';

export interface Location {
  id: string;
  name: string;
  city: string;
  state: string;
  country: string;
  latitude: number;
  longitude: number;
  grid_id?: string;
}

export interface RiskPrediction {
  location_id: string;
  risk_type: string;
  risk_score: number;
  risk_level: RiskLevel;
  confidence: number;
  trend: TrendDirection;
  explanation: string[];
  model_version: string;
  calculated_at: string;
}

export interface TrendItem {
  condition: string;
  current: number;
  previous: number;
  change_percent: number;
  direction: TrendDirection;
}

export interface TrendsResponse {
  location_id: string;
  period_days: number;
  trends: TrendItem[];
}

export interface Alert {
  id: string;
  type: string;
  severity: AlertSeverity;
  location_id?: string;
  title: string;
  message: string;
  risk_score?: number;
  is_active: boolean;
  created_at: string;
}

export interface HeatmapPoint {
  grid_id: string;
  location_id: string;
  location_name: string;
  latitude: number;
  longitude: number;
  risk_score: number;
  risk_level: RiskLevel;
  value?: number;
  label?: string;
}

export interface HeatmapResponse {
  layer: string;
  points: HeatmapPoint[];
}

export interface HistoryResponse {
  location: string;
  location_id: string;
  period: string;
  health: Record<string, number>;
  environment: Record<string, number | null>;
  health_series?: Record<string, Array<{ timestamp: string; value: number }>>;
  environment_series?: Record<string, Array<{ timestamp: string; value: number }>>;
}

export interface Sensor {
  id: string;
  sensor_code: string;
  name: string;
  type: string;
  latitude: number;
  longitude: number;
  status: 'ONLINE' | 'OFFLINE' | 'WARNING';
  last_seen?: string;
  location_id?: string;
}

export interface AdminStats {
  total_users: number;
  total_health_reports: number;
  total_sensors: number;
  online_sensors: number;
  offline_sensors: number;
  total_env_readings: number;
  active_alerts: number;
}

export interface HealthReportForm {
  symptoms: string[];
  severity: 'mild' | 'moderate' | 'severe';
  age_group?: string;
  latitude: number;
  longitude: number;
}
