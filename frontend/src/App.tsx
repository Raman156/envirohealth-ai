import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AppLayout } from './layouts/AppLayout';
import { LandingPage } from './pages/LandingPage';
import { DashboardPage } from './pages/DashboardPage';
import { MapPage } from './pages/MapPage';
import { TrendsPage } from './pages/TrendsPage';
import { HistoryPage } from './pages/HistoryPage';
import { ReportPage } from './pages/ReportPage';
import { AlertsPage } from './pages/AlertsPage';
import { AdminPage } from './pages/AdminPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

const WithLayout = ({ children }: { children: React.ReactNode }) => (
  <AppLayout>{children}</AppLayout>
);

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/dashboard" element={<WithLayout><DashboardPage /></WithLayout>} />
          <Route path="/map" element={<WithLayout><MapPage /></WithLayout>} />
          <Route path="/trends" element={<WithLayout><TrendsPage /></WithLayout>} />
          <Route path="/history" element={<WithLayout><HistoryPage /></WithLayout>} />
          <Route path="/report" element={<WithLayout><ReportPage /></WithLayout>} />
          <Route path="/alerts" element={<WithLayout><AlertsPage /></WithLayout>} />
          <Route path="/admin" element={<WithLayout><AdminPage /></WithLayout>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
