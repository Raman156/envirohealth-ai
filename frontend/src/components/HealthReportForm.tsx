import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { CheckCircle, Loader2 } from 'lucide-react';
import { healthReportsApi } from '@/services/api/healthReports';
import { useBrowserLocation } from '@/hooks/useLocation';
import clsx from 'clsx';

const SYMPTOMS = [
  { id: 'fever', label: 'Fever' },
  { id: 'cough', label: 'Cough' },
  { id: 'cold', label: 'Cold' },
  { id: 'headache', label: 'Headache' },
  { id: 'vomiting', label: 'Vomiting' },
  { id: 'diarrhea', label: 'Diarrhea' },
  { id: 'breathing_difficulty', label: 'Breathing difficulty' },
  { id: 'skin_irritation', label: 'Skin irritation' },
  { id: 'fatigue', label: 'Fatigue' },
  { id: 'body_pain', label: 'Body pain' },
];

const SEVERITY = [
  { id: 'mild', label: 'Mild' },
  { id: 'moderate', label: 'Moderate' },
  { id: 'severe', label: 'Severe' },
];

export function HealthReportForm() {
  const { coords } = useBrowserLocation();
  const [selectedSymptoms, setSelectedSymptoms] = useState<string[]>([]);
  const [severity, setSeverity] = useState<string>('mild');
  const [submitted, setSubmitted] = useState(false);

  const mutation = useMutation({
    mutationFn: healthReportsApi.submit,
    onSuccess: () => {
      setSubmitted(true);
      setSelectedSymptoms([]);
      setSeverity('mild');
    },
  });

  const toggleSymptom = (id: string) => {
    setSelectedSymptoms(prev =>
      prev.includes(id) ? prev.filter(s => s !== id) : [...prev, id]
    );
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!coords || selectedSymptoms.length === 0) return;
    mutation.mutate({
      symptoms: selectedSymptoms,
      severity: severity as any,
      latitude: coords.lat,
      longitude: coords.lng,
    });
  };

  if (submitted) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <CheckCircle size={48} className="text-green-500 mb-4" />
        <h3 className="text-lg font-semibold text-gray-800 mb-2">Thank you.</h3>
        <p className="text-gray-500 max-w-sm text-sm">
          Your anonymous report helps identify emerging health patterns in your community.
        </p>
        <button
          onClick={() => setSubmitted(false)}
          className="mt-6 text-sm text-brand-600 hover:text-brand-700 underline"
        >
          Submit another report
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <p className="text-sm font-medium text-gray-700 mb-3">How are you feeling today?</p>
        <div className="grid grid-cols-2 gap-2">
          {SYMPTOMS.map(({ id, label }) => (
            <label key={id} className={clsx(
              'flex items-center gap-2 p-2.5 rounded-lg border cursor-pointer transition-all text-sm',
              selectedSymptoms.includes(id)
                ? 'border-brand-500 bg-brand-50 text-brand-700'
                : 'border-gray-200 text-gray-600 hover:border-gray-300'
            )}>
              <input
                type="checkbox"
                className="accent-brand-500"
                checked={selectedSymptoms.includes(id)}
                onChange={() => toggleSymptom(id)}
              />
              {label}
            </label>
          ))}
        </div>
      </div>

      <div>
        <p className="text-sm font-medium text-gray-700 mb-2">Severity</p>
        <div className="flex gap-3">
          {SEVERITY.map(({ id, label }) => (
            <label key={id} className={clsx(
              'flex-1 text-center py-2 rounded-lg border cursor-pointer transition-all text-sm',
              severity === id
                ? 'border-brand-500 bg-brand-50 text-brand-700 font-medium'
                : 'border-gray-200 text-gray-600 hover:border-gray-300'
            )}>
              <input
                type="radio"
                name="severity"
                className="sr-only"
                value={id}
                checked={severity === id}
                onChange={() => setSeverity(id)}
              />
              {label}
            </label>
          ))}
        </div>
      </div>

      {mutation.error && (
        <p className="text-sm text-red-500">{(mutation.error as Error).message}</p>
      )}

      {!coords && (
        <p className="text-xs text-amber-600 bg-amber-50 p-2 rounded">
          Location access is needed to associate your report with your area.
        </p>
      )}

      <button
        type="submit"
        disabled={selectedSymptoms.length === 0 || !coords || mutation.isPending}
        className={clsx(
          'w-full py-3 rounded-xl font-semibold text-white transition-all flex items-center justify-center gap-2',
          selectedSymptoms.length > 0 && coords
            ? 'bg-brand-600 hover:bg-brand-700'
            : 'bg-gray-300 cursor-not-allowed'
        )}
      >
        {mutation.isPending ? (
          <><Loader2 size={16} className="animate-spin" /> Submitting...</>
        ) : (
          'Submit Anonymous Report'
        )}
      </button>

      <p className="text-xs text-gray-400 text-center">
        No personal information is collected. Reports are anonymized and aggregated.
      </p>
    </form>
  );
}
