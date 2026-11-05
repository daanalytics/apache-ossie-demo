export function asNumber(value: unknown): number | null {
  if (value == null || value === "") return null;
  const number = typeof value === "number" ? value : Number(value);
  return Number.isFinite(number) ? number : null;
}

export function formatValue(value: unknown): string {
  if (value == null || value === "") return "";
  if (value instanceof Date) return value.toISOString().slice(0, 10);
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

export function formatNumber(value: number | null, decimals: number): string {
  if (value == null) return "";
  return value.toLocaleString("en-US", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

export function decimalsFor(metric: string): number {
  return metric === "AVERAGE_ORDER_VALUE" ? 2 : 0;
}

export function dimensionKey(value: unknown): string {
  if (value instanceof Date) return value.toISOString().slice(0, 10);
  if (value == null) return "";
  const text = String(value);
  const date = text.match(/^(\d{4}-\d{2}-\d{2})/);
  return date ? date[1] : text;
}
