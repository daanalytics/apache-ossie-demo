import { columnTotal, hasColumns, mergeComparison, type ComparedRow } from "./merge";
import { querySnowflake, type SnowflakeRow } from "./snowflake";
import { scenarioFor, type Scenario } from "./scenarios";

export type MetricExpression = {
  name: string;
  expression: string;
  caption: string;
};

export type ComparisonResult = {
  scenario: Scenario;
  rows: ComparedRow[] | null;
  totals: { without: number; with: number; difference: number } | null;
  expression: string | null;
  related: MetricExpression[];
  caption: string | null;
  preview: SnowflakeRow[] | null;
  previewSummary: string | null;
  expressionError: string | null;
  previewError: string | null;
  queryError: string | null;
};

export function selectionCaption(expression: string): string {
  const text = expression.toLowerCase();
  if (!text.includes("order_status")) {
    return "This expression does not test order status, so every row at this grain is included.";
  }
  if (text.includes("shipped") || text.includes("processing")) {
    return "This expression selects completed, shipped, and processing orders.";
  }
  if (text.includes("completed")) {
    return "This expression selects completed orders. Any other status becomes NULL and drops out of the aggregate.";
  }
  return "This is the expression the semantic view applies.";
}

function message(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}

async function metricExpressions(metricName: string): Promise<{
  expression: string | null;
  related: MetricExpression[];
  caption: string | null;
}> {
  const definition = await querySnowflake(`
    SELECT name, expression
    FROM OSSIE_DEMO.INFORMATION_SCHEMA.SEMANTIC_METRICS
    WHERE semantic_view_name = 'ECOMMERCE_SEMANTIC_MODEL'
  `);
  const byName = new Map<string, string>();
  for (const row of definition) {
    const name = String(row.NAME ?? "");
    const expression = String(row.EXPRESSION ?? "");
    if (name) byName.set(name, expression);
  }
  const expression = byName.get(metricName) ?? null;
  if (!expression) return { expression: null, related: [], caption: null };
  const expressionText = expression.toLowerCase();
  const related = [...byName.entries()]
    .filter(([name]) => name !== metricName && expressionText.includes(name.toLowerCase()))
    .map(([name, relatedExpression]) => ({
      name: name.toLowerCase(),
      expression: relatedExpression.trim(),
      caption: selectionCaption(relatedExpression),
    }));
  return {
    expression: expression.trim(),
    related,
    caption: related.length === 0 ? selectionCaption(expression) : null,
  };
}

function previewSummary(rows: SnowflakeRow[]): string | null {
  if (rows.length === 0) return "0 rows are selected. 0 rows are left out.";
  const counted = Object.keys(rows[0]).find((column) => column.startsWith("COUNTED"));
  if (!counted) return null;
  const selected = rows.filter((row) => row[counted] != null).length;
  return `${selected} rows are selected. ${rows.length - selected} rows are left out.`;
}

export async function loadComparison(question: string | undefined): Promise<ComparisonResult> {
  const scenario = scenarioFor(question);
  const result: ComparisonResult = {
    scenario,
    rows: null,
    totals: null,
    expression: null,
    related: [],
    caption: null,
    preview: null,
    previewSummary: null,
    expressionError: null,
    previewError: null,
    queryError: null,
  };

  try {
    const expressions = await metricExpressions(scenario.metric);
    result.expression = expressions.expression;
    result.related = expressions.related;
    result.caption = expressions.caption;
  } catch (error) {
    result.expressionError = `The metric expression could not be read from the semantic view. ${message(error)}`;
  }

  try {
    result.preview = await querySnowflake(scenario.previewSql);
    result.previewSummary = previewSummary(result.preview);
  } catch (error) {
    result.previewError = `The selected rows could not be listed. ${message(error)}`;
  }

  try {
    const [withoutRows, withRows] = await Promise.all([
      querySnowflake(scenario.withoutSql),
      querySnowflake(scenario.withSql),
    ]);
    const missing = [
      ["without", withoutRows],
      ["with", withRows],
    ].filter(([, rows]) => !hasColumns(rows as SnowflakeRow[], scenario.dimension, scenario.metric));
    if (missing.length > 0) {
      result.queryError =
        `Expected columns ${scenario.dimension} and ${scenario.metric}. ` +
        `Without columns: ${Object.keys(withoutRows[0] ?? {}).join(", ") || "(none)"}. ` +
        `With columns: ${Object.keys(withRows[0] ?? {}).join(", ") || "(none)"}.`;
    } else {
      result.rows = mergeComparison(
        withoutRows,
        withRows,
        scenario.dimension,
        scenario.metric,
        scenario.sortByDimension,
      );
      if (scenario.showTotal && result.rows) {
        const without = columnTotal(result.rows, "without");
        const withValue = columnTotal(result.rows, "with");
        result.totals = { without, with: withValue, difference: without - withValue };
      }
    }
  } catch (error) {
    result.queryError = `Run 01_setup.sql and 02_semantic_view.sql first so both queries can run. Error: ${message(error)}`;
  }

  return result;
}
