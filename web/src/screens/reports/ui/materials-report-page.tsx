"use client";

import { MaterialStockReportSection } from "@/screens/reports/ui/report-sections";
import { ReportsPageShell } from "@/screens/reports/ui/reports-shell";

export function MaterialsReportPage() {
  return (
    <ReportsPageShell
      title="Складской срез"
      description="Отдельный отчет по остаткам, резервам, стоимости и проблемным позициям склада."
      content={(data) => <MaterialStockReportSection data={data} />}
    />
  );
}
