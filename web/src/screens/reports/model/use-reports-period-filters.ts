"use client";

import { useMemo, useState } from "react";

import { useOrganizationProfileQuery } from "@/entities/organization/model/use-organization-query";

function toIsoStart(value: string) {
  return value ? new Date(`${value}T00:00:00`).toISOString() : undefined;
}

function toIsoEnd(value: string) {
  return value ? new Date(`${value}T23:59:59`).toISOString() : undefined;
}

export function useReportsPeriodFilters() {
  const organizationQuery = useOrganizationProfileQuery();
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [selectedPayrollPeriodKey, setSelectedPayrollPeriodKey] = useState<string | null>("payroll-period-0");

  const selectedPayrollPeriod = useMemo(
    () =>
      organizationQuery.data?.payroll_periods_preview.find((period) => period.key === selectedPayrollPeriodKey) ?? null,
    [organizationQuery.data?.payroll_periods_preview, selectedPayrollPeriodKey]
  );

  return {
    organizationQuery,
    dateFrom,
    dateTo,
    selectedPayrollPeriod,
    selectedPayrollPeriodKey,
    setDateFrom,
    setDateTo,
    setSelectedPayrollPeriodKey,
    reset() {
      setSelectedPayrollPeriodKey("payroll-period-0");
      setDateFrom("");
      setDateTo("");
    },
    filters: {
      date_from: selectedPayrollPeriod?.date_from ?? toIsoStart(dateFrom),
      date_to: selectedPayrollPeriod?.date_to ?? toIsoEnd(dateTo)
    }
  };
}
