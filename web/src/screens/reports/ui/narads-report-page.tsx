"use client";

import { NaradsRegistryReportSection } from "@/screens/reports/ui/report-sections";
import { ReportsPageShell } from "@/screens/reports/ui/reports-shell";

export function NaradsReportPage() {
  return (
    <ReportsPageShell
      title="Реестр нарядов"
      description="Отдельный отчет по заказам на уровне наряда: статус, сроки, сумма, себестоимость и долг."
      content={(data) => <NaradsRegistryReportSection data={data} />}
    />
  );
}
