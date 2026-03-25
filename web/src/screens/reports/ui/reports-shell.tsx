"use client";

import { Alert, Group, Loader } from "@mantine/core";
import { PropsWithChildren, ReactNode } from "react";

import { useReportsQuery } from "@/entities/reports/model/use-reports-query";
import { ReportsSnapshot } from "@/entities/reports/model/types";
import { useReportsPeriodFilters } from "@/screens/reports/model/use-reports-period-filters";
import { ReportsPeriodFilterCard } from "@/screens/reports/ui/reports-period-filter-card";
import { PageHeading } from "@/shared/ui/page-heading";
import { SectionCard } from "@/shared/ui/section-card";

type ReportsPageShellProps = PropsWithChildren<{
  title: string;
  description: string;
  content: (data: ReportsSnapshot) => ReactNode;
}>;

export function ReportsPageShell({ title, description, content }: ReportsPageShellProps) {
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

  const reportsQuery = useReportsQuery(
    filters,
    {
      enabled: !selectedPayrollPeriodKey || Boolean(organizationQuery.data)
    }
  );

  return (
    <PageHeading title={title} description={description}>
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
        <Alert color="red" title="Отчет недоступен">
          Не удалось загрузить данные отчета.
        </Alert>
      ) : (
        content(reportsQuery.data)
      )}
    </PageHeading>
  );
}
