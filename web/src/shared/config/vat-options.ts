export const vatOptions = [
  { value: "without_vat", label: "Без налога (НДС)" },
  { value: "vat_0", label: "НДС 0%" },
  { value: "vat_5", label: "НДС 5%" },
  { value: "vat_7", label: "НДС 7%" },
  { value: "vat_10", label: "НДС 10%" },
  { value: "vat_20", label: "НДС 20%" }
] as const;

export type VatMode = (typeof vatOptions)[number]["value"];
