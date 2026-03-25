"use client";

import { Button, Group, Select, Stack, Text, TextInput } from "@mantine/core";

import { PayrollPeriodPreview } from "@/entities/organization/model/types";
import { SectionCard } from "@/shared/ui/section-card";

type ReportsPeriodFilterCardProps = {
  payrollPeriods: PayrollPeriodPreview[];
  selectedPayrollPeriodKey: string | null;
  selectedPayrollPeriodLabel?: string | null;
  dateFrom: string;
  dateTo: string;
  isPresetSelected: boolean;
  onSelectedPayrollPeriodKeyChange: (value: string | null) => void;
  onDateFromChange: (value: string) => void;
  onDateToChange: (value: string) => void;
  onReset: () => void;
};

export function ReportsPeriodFilterCard({
  payrollPeriods,
  selectedPayrollPeriodKey,
  selectedPayrollPeriodLabel,
  dateFrom,
  dateTo,
  isPresetSelected,
  onSelectedPayrollPeriodKeyChange,
  onDateFromChange,
  onDateToChange,
  onReset
}: ReportsPeriodFilterCardProps) {
  return (
    <SectionCard padding="lg">
      <Stack gap="sm">
        <Group align="end" wrap="wrap">
          <Select
            label="Расчетный период ЗП"
            placeholder="Свои даты"
            clearable
            data={payrollPeriods.map((period) => ({ value: period.key, label: period.label }))}
            value={selectedPayrollPeriodKey}
            onChange={onSelectedPayrollPeriodKeyChange}
          />
          <TextInput
            label="Дата от"
            type="date"
            value={dateFrom}
            onChange={(event) => onDateFromChange(event.currentTarget.value)}
            disabled={isPresetSelected}
          />
          <TextInput
            label="Дата до"
            type="date"
            value={dateTo}
            onChange={(event) => onDateToChange(event.currentTarget.value)}
            disabled={isPresetSelected}
          />
          <Button variant="light" onClick={onReset}>
            Сбросить
          </Button>
        </Group>
        {selectedPayrollPeriodLabel ? (
          <Text c="dimmed" size="sm">
            Отчеты рассчитаны по периоду {selectedPayrollPeriodLabel.replace(/^Текущий:\s*/, "")}.
          </Text>
        ) : null}
      </Stack>
    </SectionCard>
  );
}
