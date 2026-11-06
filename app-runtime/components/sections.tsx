import {
  AFTER,
  BEFORE,
  MAPPING,
  RELATIONSHIP_SQL,
  RELATIONSHIP_YAML,
  REVENUE_SQL,
  REVENUE_YAML,
  SECTION_NOTES,
  YAML,
  YAML_SECTIONS,
  type YamlSection,
} from "@/lib/content";
import { decimalsFor, formatNumber, formatValue } from "@/lib/format";
import type { ComparisonResult } from "@/lib/compare";
import { SCENARIOS } from "@/lib/scenarios";
import { ComparisonChart } from "./chart";
import { QuestionSelect } from "./question-select";

function Code({ children }: { children: string }) {
  return <pre><code>{children}</code></pre>;
}

export function About() {
  return (
    <div className="grid two">
      <div>
        <h2>The Problem: Metric Chaos</h2>
        <p>Every organization faces the same challenge:</p>
        <blockquote>
          <p>
            <em>Monthly Active Users</em> is defined <strong>differently</strong> in your CRM, your data warehouse,
            your BI tool, and your AI agent.
          </p>
        </blockquote>
        <p>
          When a human analyst or an AI agent runs a query, they should not have to guess which definition is
          correct. Yet today, the same business concept lives in dozens of incompatible formats across the data stack.
        </p>
        <h2>The Solution: Apache Ossie</h2>
        <p>
          <strong>Apache Ossie</strong> is an open specification for semantic layer and ontology. It defines a{" "}
          <strong>vendor-neutral YAML format</strong> for expressing:
        </p>
        <ul>
          <li><strong>Metrics</strong> — unambiguous business measures (Revenue, AOV, Churn Rate)</li>
          <li><strong>Dimensions</strong> — attributes to slice and filter by (Region, Segment, Date)</li>
          <li><strong>Relationships</strong> — how entities connect (orders → customers → products)</li>
          <li><strong>Business rules</strong> — the intent and context behind the data</li>
        </ul>
        <p>
          Any tool — BI platform, query engine, or AI agent — can consume and produce Ossie definitions{" "}
          <strong>without loss of meaning</strong>.
        </p>
        <h2>Why &quot;Ossie&quot;?</h2>
        <p>
          The project was originally named <em>Open Semantic Interchange (OSI)</em>, but was renamed to avoid
          confusion with other open-source projects sharing that acronym.
        </p>
        <p>
          The mascot is a <strong>kangaroo</strong> — carrying semantic metadata in its pouch as it hops between
          systems in the data stack. The specification and YAML format are unchanged; only the name and governance
          home have evolved.
        </p>
      </div>
      <aside className="grid">
        <div className="card facts">
          <h3>Quick Facts</h3>
          <div><strong>50+</strong><div className="muted">Contributing organizations</div></div>
          <div><strong>100+</strong><div className="muted">Commits since Nov 2025</div></div>
          <div><strong>35+</strong><div className="muted">Merged pull requests</div></div>
        </div>
        <div className="note">
          <h3>Governance</h3>
          <p>
            <strong>Apache Software Foundation.</strong> Vendor-neutral, open governance. No single company controls
            the standard.
          </p>
        </div>
        <div className="card">
          <h3>Key Contributors</h3>
          <ul>
            {["Snowflake", "Salesforce", "Databricks", "dbt Labs", "RelationalAI", "GoodData", "Honeydew"].map((name) => (
              <li key={name}>{name}</li>
            ))}
          </ul>
        </div>
      </aside>
    </div>
  );
}

export function YamlSpec({ section }: { section: YamlSection }) {
  const note = SECTION_NOTES[section];
  return (
    <section>
      <h2>Ossie YAML Specification — Annotated Example</h2>
      <p>
        Below is a complete Ossie semantic model for an e-commerce domain. This single YAML file serves as the{" "}
        <strong>source of truth</strong> that any tool can consume.
      </p>
      <div className="choice" role="navigation" aria-label="YAML sections">
        {YAML_SECTIONS.map((item) => (
          <a key={item} href={`?tab=yaml&section=${encodeURIComponent(item)}`} aria-current={item === section ? "page" : undefined}>
            {item}
          </a>
        ))}
      </div>
      <Code>{YAML[section]}</Code>
      {note ? <p className="note">{note}</p> : null}
    </section>
  );
}

export function Mapping() {
  return (
    <section>
      <h2>How Ossie Maps to Snowflake Semantic Views</h2>
      <p>
        Snowflake&apos;s <strong>Semantic Views</strong> are a native implementation that aligns with Ossie&apos;s vision.
        The mapping is nearly 1:1 — an Ossie YAML can be converted to a Snowflake Semantic View (and vice versa) with
        minimal transformation.
      </p>
      <h3>Concept Mapping</h3>
      <div className="table-wrap">
        <table>
          <thead>
            <tr><th>Ossie Concept</th><th>Snowflake Equivalent</th><th>Purpose</th></tr>
          </thead>
          <tbody>
            {MAPPING.map(([concept, equivalent, purpose]) => (
              <tr key={concept}><td>{concept}</td><td>{equivalent}</td><td>{purpose}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
      <h3>Side-by-Side: Ossie YAML vs Snowflake SQL</h3>
      <div className="grid split">
        <div><h3>Ossie YAML</h3><Code>{REVENUE_YAML}</Code></div>
        <div><h3>Snowflake Semantic View</h3><Code>{REVENUE_SQL}</Code></div>
        <div><h3>Ossie YAML</h3><Code>{RELATIONSHIP_YAML}</Code></div>
        <div>
          <h3>Snowflake Semantic View</h3>
          <Code>{RELATIONSHIP_SQL}</Code>
          <p className="caption">
            Many orders belong to one customer because customer_id is the primary key of customers. Snowflake infers
            that cardinality from the key.
          </p>
        </div>
      </div>
      <h3>Reference Implementations (Converters)</h3>
      <div className="table-wrap">
        <table>
          <thead><tr><th>Converter</th><th>Direction</th><th>Status</th></tr></thead>
          <tbody>
            <tr><td>Ossie → Snowflake Semantic Model</td><td>Ossie YAML → Snowflake</td><td>Available</td></tr>
            <tr><td>Ossie → dbt MetricFlow</td><td>Ossie YAML → dbt metrics</td><td>Available</td></tr>
            <tr><td>Apache Polaris → Ossie</td><td>Polaris catalog → Ossie YAML</td><td>Available</td></tr>
            <tr><td>Snowflake → Ossie</td><td>Snowflake Semantic View → Ossie YAML</td><td>Planned</td></tr>
          </tbody>
        </table>
      </div>
      <p>This means you can define metrics <strong>once</strong> in Ossie format and deploy to multiple platforms.</p>
    </section>
  );
}

export function Compare({ result }: { result: ComparisonResult }) {
  const { scenario } = result;
  const decimals = decimalsFor(scenario.metric);
  const dimensionLabel = scenario.dimension.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
  return (
    <section>
      <h2>Same question, two answers</h2>
      <p>
        The left query reads the base tables and invents the metric. The right query asks the semantic view for the
        metric by name. The chart is the difference.
      </p>
      <QuestionSelect question={scenario.question} options={SCENARIOS.map((item) => item.question)} />
      <div className="grid split">
        <div>
          <h3>Without a semantic view</h3>
          <p className="caption">{scenario.withoutNote}</p>
          <Code>{scenario.withoutSql}</Code>
        </div>
        <div>
          <h3>With the semantic view</h3>
          <p className="caption">{scenario.withNote}</p>
          <p><strong>Generated query</strong></p>
          <Code>{scenario.withSql}</Code>
          {result.expressionError ? <p className="caption">{result.expressionError}</p> : null}
          {result.expression ? (
            <>
              <p><strong>Expression the view applies</strong></p>
              <Code>{result.expression}</Code>
              {result.related.length > 0 ? (
                <>
                  <p className="caption">This metric uses the expressions below, and those expressions select the rows.</p>
                  {result.related.map((related) => (
                    <div key={related.name}>
                      <p><strong>{related.name}</strong></p>
                      <Code>{related.expression}</Code>
                      <p className="caption">{related.caption}</p>
                    </div>
                  ))}
                </>
              ) : result.caption ? <p className="caption">{result.caption}</p> : null}
            </>
          ) : null}
        </div>
      </div>
      <h3>Rows this metric selects</h3>
      {result.previewError ? <p className="caption">{result.previewError}</p> : null}
      {result.previewSummary ? <p className="caption">{result.previewSummary}</p> : null}
      {result.preview ? <DataTable rows={result.preview} /> : null}
      {result.queryError ? <p className="warn">{result.queryError}</p> : null}
      {result.totals ? (
        <div className="metrics">
          <div className="card metric"><span>Without a semantic view</span><strong>{formatNumber(result.totals.without, 0)}</strong></div>
          <div className="card metric"><span>With the semantic view</span><strong>{formatNumber(result.totals.with, 0)}</strong></div>
          <div className="card metric"><span>Difference</span><strong>{formatNumber(result.totals.difference, 0)}</strong></div>
        </div>
      ) : null}
      {result.rows && result.rows.length > 0 ? (
        <>
          <div className="legend">
            <span><i className="swatch" style={{ background: "#7eb6ff" }} />Without semantic view</span>
            <span><i className="swatch" style={{ background: "#1f6feb" }} />With semantic view</span>
          </div>
          <ComparisonChart rows={result.rows} kind={scenario.chart} />
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>{dimensionLabel}</th>
                  <th className="num">Without semantic view</th>
                  <th className="num">With semantic view</th>
                  <th className="num">Difference</th>
                </tr>
              </thead>
              <tbody>
                {result.rows.map((row) => (
                  <tr key={row.dimension}>
                    <td>{row.dimension}</td>
                    <td className="num">{formatNumber(row.without, decimals)}</td>
                    <td className="num">{formatNumber(row.with, decimals)}</td>
                    <td className="num">{formatNumber(row.difference, decimals)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      ) : null}
    </section>
  );
}

function DataTable({ rows }: { rows: Record<string, unknown>[] }) {
  const columns = Object.keys(rows[0] ?? {});
  if (columns.length === 0) return <p className="caption">No rows.</p>;
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>{columns.map((column) => <th key={column}>{column}</th>)}</tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={index}>
              {columns.map((column) => <td key={column}>{formatValue(row[column])}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function Vision() {
  return (
    <section>
      <h2>The Interoperability Vision</h2>
      <h3>Before Ossie: Fragmented Semantic Definitions</h3>
      <Code>{BEFORE}</Code>
      <h3>After Ossie: One Definition, Many Consumers</h3>
      <Code>{AFTER}</Code>
      <div className="grid split">
        <div className="card">
          <h3>Vendor Neutrality</h3>
          <ul>
            <li>No single company controls the spec</li>
            <li>Committership earned through contribution</li>
            <li>Public mailing lists and GitHub development</li>
            <li>Formal vote process for spec changes</li>
          </ul>
        </div>
        <div className="card">
          <h3>Enterprise Confidence</h3>
          <ul>
            <li>ASF governance is proven (Spark, Kafka, Iceberg...)</li>
            <li>IP protection via Apache License 2.0</li>
            <li>Long-term sustainability</li>
            <li>Cross-industry adoption</li>
          </ul>
        </div>
      </div>
      <h3>What&apos;s on the Roadmap?</h3>
      <ul>
        <li><strong>Deeper spec expressiveness</strong> — Advanced metric logic, windowing functions, complex relationships</li>
        <li><strong>More platform converters</strong> — Adopt Ossie without ripping out existing tools</li>
        <li><strong>Standardized semantic query spec</strong> — A universal query language any engine can support</li>
        <li><strong>Apache Polaris integration</strong> — Semantic models discoverable directly from the catalog</li>
      </ul>
      <h3>Get Involved</h3>
      <div className="grid three">
        <div className="card"><h3>Website</h3><a href="https://ossie.apache.org">ossie.apache.org</a></div>
        <div className="card">
          <h3>Slack</h3>
          <a href="https://join.slack.com/t/apache-ossie/shared_invite/zt-42i1xkgy8-7YQtKEDq7v~mceFmdiLhkA">apache-ossie.slack.com</a>
        </div>
        <div className="card">
          <h3>Blog Post</h3>
          <a href="https://www.snowflake.com/en/blog/apache-ossie-open-semantic-interchange-incubator/">Snowflake Announcement</a>
        </div>
      </div>
    </section>
  );
}
