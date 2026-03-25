"use client";

import { PayrollOperationsReportSection } from "@/screens/reports/ui/report-sections";
import { ReportsPageShell } from "@/screens/reports/ui/reports-shell";

export function PayrollOperationsReportPage() {
  return (
    <ReportsPageShell
      title="Операции по нарядам"
      description="Отдельный отчет с детализацией начислений по техникам и конкретным операциям."
      content={(data) => <PayrollOperationsReportSection data={data} />}
    />
  );
}
