import { Card, CardBody } from '@/components/ui/Card';
import { HealthReportForm } from '@/components/HealthReportForm';
import { ShieldCheck } from 'lucide-react';

export function ReportPage() {
  return (
    <div className="max-w-lg mx-auto space-y-4">
      <div>
        <h1 className="text-xl font-bold text-gray-900">Report Symptoms</h1>
        <p className="text-sm text-gray-500 mt-0.5">Your anonymous report contributes to early detection of community health patterns.</p>
      </div>

      <div className="flex items-start gap-2 bg-blue-50 border border-blue-100 rounded-xl p-3">
        <ShieldCheck size={16} className="text-blue-500 mt-0.5 shrink-0" />
        <p className="text-xs text-blue-700">
          This form is completely anonymous. No name, phone number, or email is collected.
          Reports are aggregated by area — individual submissions are never shown publicly.
        </p>
      </div>

      <div className="bg-amber-50 border border-amber-100 rounded-xl p-3">
        <p className="text-xs text-amber-700">
          <strong>Important:</strong> This is not a medical diagnosis tool. If you have a medical emergency,
          please contact emergency services immediately.
        </p>
      </div>

      <Card>
        <CardBody className="pt-5">
          <HealthReportForm />
        </CardBody>
      </Card>
    </div>
  );
}
