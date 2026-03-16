"use client";

import { useDashboardQuery } from "@/entities/dashboard/model/use-dashboard-query";
import { DashboardOverview } from "@/widgets/dashboard-overview/ui/dashboard-overview";
import { PageHeading } from "@/shared/ui/page-heading";

export function DashboardPage() {
  const dashboardQuery = useDashboardQuery();

  return (
    <PageHeading
      title="Сводка"
      description="Главный обзор лаборатории: загрузка, прибыльность, просрочки и самые ценные клиенты."
    >
      <DashboardOverview
        data={dashboardQuery.data}
        isError={dashboardQuery.isError}
        isLoading={dashboardQuery.isLoading}
      />
    </PageHeading>
  );
}
