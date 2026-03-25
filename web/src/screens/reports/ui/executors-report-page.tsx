"use client";

import { ExecutorLoadReportSection } from "@/screens/reports/ui/report-sections";
import { ReportsPageShell } from "@/screens/reports/ui/reports-shell";

export function ExecutorsReportPage() {
  return (
    <ReportsPageShell
      title="Исполнители"
      description="Отдельный отчет по текущей загрузке, закрытым работам и начислениям исполнителей."
      content={(data) => <ExecutorLoadReportSection data={data} />}
    />
  );
}
