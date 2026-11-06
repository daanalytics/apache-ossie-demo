import { About, Compare, Mapping, Vision, YamlSpec } from "@/components/sections";
import { loadComparison } from "@/lib/compare";
import { TABS, sectionFrom, tabFrom } from "@/lib/content";

export const dynamic = "force-dynamic";

type Search = Record<string, string | string[] | undefined>;

function first(value: string | string[] | undefined): string | undefined {
  return Array.isArray(value) ? value[0] : value;
}

export default async function Page({ searchParams }: { searchParams: Promise<Search> }) {
  const params = await searchParams;
  const tab = tabFrom(first(params.tab));
  const section = sectionFrom(first(params.section));
  const comparison = tab === "compare" ? await loadComparison(first(params.question)) : null;

  return (
    <main className="page">
      <header>
        <h1>Apache Ossie (Incubating) + Snowflake</h1>
        <p>An open specification for semantic interoperability — and how Snowflake implements it natively</p>
      </header>
      <nav aria-label="Demo sections">
        {TABS.map((item) => (
          <a key={item.id} href={`?tab=${item.id}`} aria-current={item.id === tab ? "page" : undefined}>
            {item.label}
          </a>
        ))}
      </nav>
      {tab === "about" ? <About /> : null}
      {tab === "yaml" ? <YamlSpec section={section} /> : null}
      {tab === "mapping" ? <Mapping /> : null}
      {tab === "compare" && comparison ? <Compare result={comparison} /> : null}
      {tab === "vision" ? <Vision /> : null}
      <footer>
        Built with Snowflake App Runtime | Apache Ossie is currently undergoing incubation at The Apache Software Foundation.
      </footer>
    </main>
  );
}
