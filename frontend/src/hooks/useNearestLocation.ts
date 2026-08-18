import { useQuery } from '@tanstack/react-query';
import { locationsApi } from '@/services/api/locations';
import { useBrowserLocation } from './useLocation';

export function useNearestLocation() {
  const { coords } = useBrowserLocation();

  return useQuery({
    queryKey: ['nearest-location', coords?.lat, coords?.lng],
    queryFn: () => locationsApi.getNearby(coords!.lat, coords!.lng, 50),
    enabled: !!coords,
    select: (data) => data[0] ?? null,
    staleTime: 5 * 60 * 1000,
  });
}
