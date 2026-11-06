import type { ComparedRow } from "@/lib/merge";

const WITHOUT = "#7eb6ff";
const WITH = "#1f6feb";

export function ComparisonChart({ rows, kind }: { rows: ComparedRow[]; kind: "bar" | "line" }) {
  const width = 920;
  const height = 320;
  const pad = { top: 16, right: 16, bottom: 72, left: 64 };
  const innerW = width - pad.left - pad.right;
  const innerH = height - pad.top - pad.bottom;
  const max = Math.max(1, ...rows.flatMap((row) => [row.without ?? 0, row.with ?? 0]));
  const y = (value: number) => pad.top + innerH - (value / max) * innerH;
  const ticks = [0, max / 2, max];

  const barGroup = innerW / Math.max(rows.length, 1);
  const barWidth = Math.min(28, barGroup * 0.32);

  const points = (field: "without" | "with") =>
    rows
      .map((row, index) => {
        const x = pad.left + barGroup * index + barGroup / 2;
        return `${x},${y(row[field] ?? 0)}`;
      })
      .join(" ");

  return (
    <svg className="chart" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Comparison chart">
      {ticks.map((tick) => (
        <g key={tick}>
          <line x1={pad.left} x2={width - pad.right} y1={y(tick)} y2={y(tick)} stroke="#2a4a68" />
          <text x={pad.left - 8} y={y(tick) + 4} fill="#9bb3c7" fontSize="11" textAnchor="end">
            {compact(tick)}
          </text>
        </g>
      ))}
      {kind === "bar"
        ? rows.map((row, index) => {
            const center = pad.left + barGroup * index + barGroup / 2;
            return (
              <g key={row.dimension}>
                <rect
                  x={center - barWidth - 2}
                  y={y(row.without ?? 0)}
                  width={barWidth}
                  height={pad.top + innerH - y(row.without ?? 0)}
                  fill={WITHOUT}
                  rx="3"
                />
                <rect
                  x={center + 2}
                  y={y(row.with ?? 0)}
                  width={barWidth}
                  height={pad.top + innerH - y(row.with ?? 0)}
                  fill={WITH}
                  rx="3"
                />
                <Label x={center} y={height - 58} text={row.dimension} />
              </g>
            );
          })
        : (
          <>
            <polyline fill="none" stroke={WITHOUT} strokeWidth="3" points={points("without")} />
            <polyline fill="none" stroke={WITH} strokeWidth="3" points={points("with")} />
            {rows.map((row, index) => (
              <Label
                key={row.dimension}
                x={pad.left + barGroup * index + barGroup / 2}
                y={height - 58}
                text={row.dimension}
              />
            ))}
          </>
        )}
    </svg>
  );
}

function Label({ x, y, text }: { x: number; y: number; text: string }) {
  const shown = text.length > 16 ? `${text.slice(0, 15)}…` : text;
  return (
    <text x={x} y={y} fill="#9bb3c7" fontSize="11" textAnchor="end" transform={`rotate(-35 ${x} ${y})`}>
      {shown}
    </text>
  );
}

function compact(value: number): string {
  if (value >= 1000) return `${Math.round(value / 100) / 10}k`;
  return String(Math.round(value));
}
