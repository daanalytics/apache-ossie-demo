import { readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import snowflake from "snowflake-sdk";

export type SnowflakeRow = Record<string, unknown>;

export type QueryOptions = {
  binds?: snowflake.Binds;
  warehouse?: string;
  callersRights?: boolean;
};

const TOKEN_PATH = "/snowflake/session/token";

snowflake.configure({
  logLevel: "ERROR",
  ocspFailOpen: true,
  disableOCSPChecks: process.env.SNOWFLAKE_INSECURE_MODE === "true",
});

function tomlValue(raw: string): string {
  const value = raw.trim();
  if (
    (value.startsWith('"') && value.endsWith('"')) ||
    (value.startsWith("'") && value.endsWith("'"))
  ) {
    return value.slice(1, -1);
  }
  return value;
}

function readConnectionFile(): Record<string, string> {
  const candidates = [
    process.env.SNOWFLAKE_CONNECTIONS_FILE,
    join(homedir(), ".snowflake", "connections.toml"),
    join(homedir(), ".snowflake", "config.toml"),
  ].filter((path): path is string => Boolean(path));

  for (const path of candidates) {
    let text: string;
    try {
      text = readFileSync(path, "utf8");
    } catch {
      continue;
    }
    const sections = new Map<string, Record<string, string>>();
    let current = "default";
    for (const raw of text.split(/\r?\n/)) {
      const line = raw.trim();
      if (!line || line.startsWith("#")) continue;
      const header = line.match(/^\[(.+)]$/);
      if (header) {
        current = header[1];
        if (!sections.has(current)) sections.set(current, {});
        continue;
      }
      const eq = line.indexOf("=");
      if (eq < 0) continue;
      if (!sections.has(current)) sections.set(current, {});
      sections.get(current)![line.slice(0, eq).trim()] = tomlValue(line.slice(eq + 1));
    }
    const preferred =
      process.env.SNOWFLAKE_CONNECTION_NAME ??
      sections.get("default")?.default_connection_name ??
      "default";
    return sections.get(preferred) ?? sections.values().next().value ?? {};
  }
  return {};
}

function sessionToken(): string | null {
  try {
    const token = readFileSync(TOKEN_PATH, "utf8").trim();
    return token || null;
  } catch {
    return null;
  }
}

function connectionOptions(warehouse?: string): snowflake.ConnectionOptions {
  const file = readConnectionFile();
  const account = process.env.SNOWFLAKE_ACCOUNT || file.account;
  const host = process.env.SNOWFLAKE_HOST || file.host;
  const user = process.env.SNOWFLAKE_USER || file.user;
  const password = process.env.SNOWFLAKE_PASSWORD || file.password;
  const token = sessionToken();

  if (!account && !host) {
    throw new Error(
      "No Snowflake connection found. Deployed apps use /snowflake/session/token. Locally, set SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, and SNOWFLAKE_PASSWORD, or add a connection under ~/.snowflake/connections.toml.",
    );
  }

  const options = {
    account: account ?? "",
    host,
    port: process.env.SNOWFLAKE_PORT ? Number(process.env.SNOWFLAKE_PORT) : undefined,
    protocol: process.env.SNOWFLAKE_PROTOCOL,
    warehouse: warehouse || process.env.SNOWFLAKE_WAREHOUSE || file.warehouse,
    database: process.env.SNOWFLAKE_DATABASE || file.database || "OSSIE_DEMO",
    schema: process.env.SNOWFLAKE_SCHEMA || file.schema || "ECOMMERCE",
    clientSessionKeepAlive: true,
  } as snowflake.ConnectionOptions;

  if (token) {
    options.authenticator = "OAUTH";
    options.token = token;
    // No username with the session token: Snowflake takes the identity from the
    // token, and any username that differs from it is rejected.
  } else if (user && password) {
    options.username = user;
    options.password = password;
  } else {
    throw new Error(
      "Snowflake account is configured, but neither a session token nor a password is available.",
    );
  }

  return options;
}

function uppercaseRow(row: Record<string, unknown>): SnowflakeRow {
  return Object.fromEntries(Object.entries(row).map(([key, value]) => [key.toUpperCase(), value]));
}

function connect(options: snowflake.ConnectionOptions): Promise<snowflake.Connection> {
  const connection = snowflake.createConnection(options);
  return new Promise((resolve, reject) => {
    connection.connect((error) => (error ? reject(error) : resolve(connection)));
  });
}

function execute(connection: snowflake.Connection, sqlText: string, binds?: snowflake.Binds) {
  return new Promise<SnowflakeRow[]>((resolve, reject) => {
    connection.execute({
      sqlText,
      binds,
      complete: (error, _statement, rows) => {
        if (error) reject(error);
        else resolve((rows ?? []).map((row) => uppercaseRow(row as Record<string, unknown>)));
      },
    });
  });
}

export async function querySnowflake(sqlText: string, options: QueryOptions = {}): Promise<SnowflakeRow[]> {
  const connectionOptionsWithWarehouse = connectionOptions(options.warehouse);
  if (options.callersRights) {
    const { headers } = await import("next/headers");
    const callerToken = (await headers()).get("sf-context-current-user-token");
    if (callerToken && connectionOptionsWithWarehouse.token) {
      connectionOptionsWithWarehouse.token = `${connectionOptionsWithWarehouse.token}.${callerToken}`;
    }
  }
  const connection = await connect(connectionOptionsWithWarehouse);
  try {
    return await execute(connection, sqlText, options.binds);
  } finally {
    connection.destroy((error) => {
      if (error) console.error("Snowflake disconnect failed", error);
    });
  }
}

export async function querySnowflakeLongRunning(
  sqlText: string,
  options: QueryOptions = {},
): Promise<SnowflakeRow[]> {
  return querySnowflake(sqlText, options);
}
