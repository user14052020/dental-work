"use client";

import { PayrollReportSection } from "@/screens/reports/ui/report-sections";
import { ReportsPageShell } from "@/screens/reports/ui/reports-shell";

export function PayrollReportPage() {
  return (
    <ReportsPageShell
      title="Оплата труда"
      description="Отдельный отчет по начислениям техникам в закрытых нарядах за выбранный период."
      content={(data) => <PayrollReportSection data={data} />}
    />
  );
}
