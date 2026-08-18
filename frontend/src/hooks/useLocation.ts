import { useState, useEffect } from 'react';

export interface GeoCoords {
  lat: number;
  lng: number;
}

export function useBrowserLocation() {
  const [coords, setCoords] = useState<GeoCoords | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const requestLocation = () => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by your browser');
      return;
    }
    setLoading(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setCoords({ lat: pos.coords.latitude, lng: pos.coords.longitude });
        setLoading(false);
      },
      (err) => {
        setError(err.message);
        setLoading(false);
        // Fall back to a default location (New Delhi)
        setCoords({ lat: 28.6139, lng: 77.2090 });
      },
      { timeout: 10000, maximumAge: 300000 }
    );
  };

  useEffect(() => {
    requestLocation();
  }, []);

  return { coords, error, loading, requestLocation };
}
