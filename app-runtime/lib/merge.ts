import { asNumber, dimensionKey } from "./format";

export type ComparedRow = {
  dimension: string;
  without: number | null;
  with: number | null;
  difference: number;
};

function column(row: Record<string, unknown>, name: string): unknown {
  const match = Object.keys(row).find((key) => key.toUpperCase() === name.toUpperCase());
  return match ? row[match] : undefined;
}

export function mergeComparison(
  withoutRows: Record<string, unknown>[],
  withRows: Record<string, unknown>[],
  dimension: string,
  metric: string,
  sortByDimension: boolean,
): ComparedRow[] {
  const merged = new Map<string, ComparedRow>();

  const add = (rows: Record<string, unknown>[], field: "without" | "with") => {
    for (const row of rows) {
      const label = dimensionKey(column(row, dimension));
      const current = merged.get(label) ?? { dimension: label, without: null, with: null, difference: 0 };
      current[field] = asNumber(column(row, metric));
      merged.set(label, current);
    }
  };

  add(withoutRows, "without");
  add(withRows, "with");

  const rows = [...merged.values()].map((row) => ({
    ...row,
    difference: (row.without ?? 0) - (row.with ?? 0),
  }));

  rows.sort((left, right) => {
    if (sortByDimension) return left.dimension.localeCompare(right.dimension);
    return (right.without ?? Number.NEGATIVE_INFINITY) - (left.without ?? Number.NEGATIVE_INFINITY);
  });
  return rows;
}

export function columnTotal(rows: ComparedRow[], field: "without" | "with" | "difference"): number {
  return rows.reduce((sum, row) => sum + (row[field] ?? 0), 0);
}

export function hasColumns(rows: Record<string, unknown>[], ...names: string[]): boolean {
  if (rows.length === 0) return true;
  const present = new Set(Object.keys(rows[0]).map((key) => key.toUpperCase()));
  return names.every((name) => present.has(name.toUpperCase()));
}
