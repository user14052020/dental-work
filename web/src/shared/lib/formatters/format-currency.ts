export function formatCurrency(value: number | string, currency = "RUB") {
  const normalized = typeof value === "number" ? value : Number(value);

  return new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency,
    maximumFractionDigits: 2
  }).format(Number.isFinite(normalized) ? normalized : 0);
}
