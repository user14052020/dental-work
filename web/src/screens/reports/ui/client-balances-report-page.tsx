"use client";

import { ClientBalancesReportSection } from "@/screens/reports/ui/report-sections";
import { ReportsPageShell } from "@/screens/reports/ui/reports-shell";

export function ClientBalancesReportPage() {
  return (
    <ReportsPageShell
      title="Баланс клиентов"
      description="Отдельный отчет по задолженности, оплатам и последней активности клиентов."
      content={(data) => <ClientBalancesReportSection data={data} />}
    />
  );
}
