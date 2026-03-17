"use client";

import { Button, Divider, Group, SegmentedControl, Stack, Text } from "@mantine/core";
import { useEffect, useState } from "react";

import {
  formatToothSelectionSummary,
  permanentOdontogramRows,
  primaryOdontogramRows,
  toothSelectionModeOptions,
  toothSurfaceOptions,
  ToothSelectionItem,
  ToothSelectionMode,
  toggleToothSurface,
  upsertToothSelectionItem
} from "@/entities/works/model/tooth-selection";
import { cn } from "@/shared/lib/cn";

type OdontogramProps = {
  value: ToothSelectionItem[];
  onChange?: (value: ToothSelectionItem[]) => void;
  readOnly?: boolean;
};

export function Odontogram({ value, onChange, readOnly = false }: OdontogramProps) {
  const [selectionMode, setSelectionMode] = useState<ToothSelectionMode>("target");
  const [activeToothCode, setActiveToothCode] = useState<string | null>(value[0]?.tooth_code ?? null);

  useEffect(() => {
    if (!value.length) {
      setActiveToothCode(null);
      return;
    }

    if (activeToothCode && value.some((item) => item.tooth_code === activeToothCode)) {
      return;
    }

    setActiveToothCode(value[0].tooth_code);
  }, [activeToothCode, value]);

  const activeTooth = value.find((item) => item.tooth_code === activeToothCode) ?? null;

  function handleToothClick(toothCode: string) {
    if (readOnly || !onChange) {
      return;
    }

    const nextItems = upsertToothSelectionItem(value, toothCode, selectionMode);
    onChange(nextItems);
    setActiveToothCode(nextItems.some((item) => item.tooth_code === toothCode) ? toothCode : nextItems[0]?.tooth_code ?? null);
  }

  function handleSurfaceClick(surface: (typeof toothSurfaceOptions)[number]["value"]) {
    if (readOnly || !onChange || !activeToothCode) {
      return;
    }

    onChange(toggleToothSurface(value, activeToothCode, surface));
  }

  function handleClear() {
    if (readOnly || !onChange) {
      return;
    }

    onChange([]);
    setActiveToothCode(null);
  }

  return (
    <Stack gap="sm">
      {!readOnly ? (
        <Group justify="space-between" gap="sm" wrap="wrap">
          <SegmentedControl
            data={toothSelectionModeOptions.map((item) => ({ ...item }))}
            size="sm"
            value={selectionMode}
            onChange={(value) => setSelectionMode(value as ToothSelectionMode)}
          />
          <Button size="xs" variant="light" onClick={handleClear}>
            Очистить формулу
          </Button>
        </Group>
      ) : null}

      <div className="rounded-[24px] border border-slate-200 bg-slate-50/80 p-4">
        <Stack gap="md">
          <OdontogramSection
            rows={permanentOdontogramRows}
            title="Постоянные зубы"
            value={value}
            activeToothCode={activeToothCode}
            readOnly={readOnly}
            onToothClick={handleToothClick}
          />
          <Divider />
          <OdontogramSection
            rows={primaryOdontogramRows}
            title="Молочные зубы"
            value={value}
            activeToothCode={activeToothCode}
            readOnly={readOnly}
            onToothClick={handleToothClick}
          />
        </Stack>
      </div>

      <Group gap="md" wrap="wrap">
        <LegendItem colorClass="bg-teal-500" label="Зуб в работе" />
        <LegendItem colorClass="bg-rose-200" label="Отсутствующий зуб" textClass="text-rose-700" />
      </Group>

      {!readOnly && activeTooth ? (
        <div className="rounded-[20px] border border-slate-200 bg-white p-4">
          <Stack gap="xs">
            <Text fw={700}>Поверхности зуба {activeTooth.tooth_code}</Text>
            <Text c="dimmed" size="sm">
              Выбери поверхности для более точной формулы и дальнейших печатных форм.
            </Text>
            <div className="flex flex-wrap gap-2">
              {toothSurfaceOptions.map((surface) => {
                const isActive = activeTooth.surfaces.includes(surface.value);
                return (
                  <button
                    key={surface.value}
                    className={cn(
                      "rounded-full border px-3 py-1.5 text-sm font-semibold transition",
                      isActive
                        ? "border-teal-600 bg-teal-600 text-white"
                        : "border-slate-200 bg-slate-50 text-slate-700 hover:border-teal-300 hover:text-teal-700"
                    )}
                    type="button"
                    onClick={() => handleSurfaceClick(surface.value)}
                  >
                    {surface.label}
                  </button>
                );
              })}
            </div>
          </Stack>
        </div>
      ) : null}

      <Text c="dimmed" size="sm">
        {value.length ? formatToothSelectionSummary(value) : "Зубная формула пока не выбрана."}
      </Text>
    </Stack>
  );
}

type OdontogramSectionProps = {
  title: string;
  rows: readonly (readonly string[])[];
  value: ToothSelectionItem[];
  activeToothCode: string | null;
  readOnly: boolean;
  onToothClick: (toothCode: string) => void;
};

function OdontogramSection({
  title,
  rows,
  value,
  activeToothCode,
  readOnly,
  onToothClick
}: OdontogramSectionProps) {
  return (
    <Stack gap="xs">
      <Text fw={700}>{title}</Text>
      {rows.map((row, index) => (
        <div key={`${title}-${index}`} className="grid gap-2" style={{ gridTemplateColumns: `repeat(${row.length}, minmax(0, 1fr))` }}>
          {row.map((toothCode) => {
            const item = value.find((selectionItem) => selectionItem.tooth_code === toothCode);
            const isActive = toothCode === activeToothCode;
            return (
              <button
                key={toothCode}
                className={cn(
                  "min-h-[56px] rounded-[18px] border px-2 py-3 text-center text-sm font-semibold transition",
                  item?.state === "target" && "border-teal-600 bg-teal-600 text-white shadow-sm",
                  item?.state === "missing" && "border-rose-300 bg-rose-100 text-rose-700 line-through",
                  !item && "border-slate-200 bg-white text-slate-700 hover:border-teal-300 hover:text-teal-700",
                  isActive && "ring-2 ring-teal-200"
                )}
                disabled={readOnly}
                type="button"
                onClick={() => onToothClick(toothCode)}
              >
                {toothCode}
              </button>
            );
          })}
        </div>
      ))}
    </Stack>
  );
}

type LegendItemProps = {
  label: string;
  colorClass: string;
  textClass?: string;
};

function LegendItem({ label, colorClass, textClass }: LegendItemProps) {
  return (
    <div className="flex items-center gap-2">
      <span className={cn("h-3 w-3 rounded-full", colorClass)} />
      <Text className={textClass} size="sm">
        {label}
      </Text>
    </div>
  );
}
