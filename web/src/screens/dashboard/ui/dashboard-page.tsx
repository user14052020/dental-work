"use client";

import { Alert, Group, Loader, Stack } from "@mantine/core";
import { useMemo } from "react";

import { useReportsQuery } from "@/entities/reports/model/use-reports-query";
import { useReportsPeriodFilters } from "@/screens/reports/model/use-reports-period-filters";
import { ReportsOverviewCards } from "@/screens/reports/ui/report-sections";
import { ReportsPeriodFilterCard } from "@/screens/reports/ui/reports-period-filter-card";
import { PageHeading } from "@/shared/ui/page-heading";
import { SectionCard } from "@/shared/ui/section-card";

export function DashboardPage() {
  const {
    organizationQuery,
    dateFrom,
    dateTo,
    selectedPayrollPeriod,
    selectedPayrollPeriodKey,
    setDateFrom,
    setDateTo,
    setSelectedPayrollPeriodKey,
    reset,
    filters
  } = useReportsPeriodFilters();

  const reportsQuery = useReportsQuery(filters, {
    enabled: !selectedPayrollPeriodKey || Boolean(organizationQuery.data)
  });
  const overdueHref = useMemo(() => {
    const params = new URLSearchParams({ status: "overdue" });
    if (dateFrom) {
      params.set("date_from", dateFrom);
    }
    if (dateTo) {
      params.set("date_to", dateTo);
    }
    return `/narads?${params.toString()}`;
  }, [dateFrom, dateTo]);

  return (
    <PageHeading
      title="Сводка"
      description="Ключевые показатели лаборатории по выбранному отчетному периоду."
    >
      <Stack gap="lg">
        <ReportsPeriodFilterCard
          payrollPeriods={organizationQuery.data?.payroll_periods_preview ?? []}
          selectedPayrollPeriodKey={selectedPayrollPeriodKey}
          selectedPayrollPeriodLabel={selectedPayrollPeriod?.label}
          dateFrom={dateFrom}
          dateTo={dateTo}
          isPresetSelected={Boolean(selectedPayrollPeriod)}
          onSelectedPayrollPeriodKeyChange={setSelectedPayrollPeriodKey}
          onDateFromChange={setDateFrom}
          onDateToChange={setDateTo}
          onReset={reset}
        />

        {reportsQuery.isLoading || organizationQuery.isLoading ? (
          <SectionCard>
            <Group justify="center" py="xl">
              <Loader />
            </Group>
          </SectionCard>
        ) : reportsQuery.isError || organizationQuery.isError || !reportsQuery.data ? (
          <Alert color="red" title="Сводка недоступна">
            Не удалось загрузить показатели за выбранный период.
          </Alert>
        ) : (
          <ReportsOverviewCards data={reportsQuery.data} overdueHref={overdueHref} />
        )}
      </Stack>
    </PageHeading>
  );
}
