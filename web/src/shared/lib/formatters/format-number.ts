export function formatNumber(value: number | string, maximumFractionDigits = 2) {
  const normalized = typeof value === "number" ? value : Number(value);

  return new Intl.NumberFormat("ru-RU", {
    maximumFractionDigits
  }).format(Number.isFinite(normalized) ? normalized : 0);
}
