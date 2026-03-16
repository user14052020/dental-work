export const materialUnitOptions = [
  { value: "gram", label: "грамм" },
  { value: "milliliter", label: "миллилитр" },
  { value: "piece", label: "штука" },
  { value: "pack", label: "упаковка" },
  { value: "hour", label: "час" }
] as const;

const materialUnitLabels = Object.fromEntries(
  materialUnitOptions.map((item) => [item.value, item.label])
) as Record<string, string>;

export function formatMaterialUnit(unit: string) {
  return materialUnitLabels[unit] ?? unit;
}
