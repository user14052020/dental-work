"use client";

import { NaradMaterialConsumptionReportSection } from "@/screens/reports/ui/report-sections";
import { ReportsPageShell } from "@/screens/reports/ui/reports-shell";

export function NaradMaterialConsumptionReportPage() {
  return (
    <ReportsPageShell
      title="Расход по нарядам"
      description="Списания материалов по закрытым нарядам и строкам заказов за выбранный период."
      content={(data) => <NaradMaterialConsumptionReportSection data={data} />}
    />
  );
}
