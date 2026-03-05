import Table from "cli-table3";
import chalk from "chalk";
import { stringify as yamlStringify } from "yaml";

export interface TableColumnDef {
  key: string;
  header: string;
  width?: number;
  // Transform value before display
  transform?: (value: unknown) => string;
}

// Format data according to output format
export function formatOutput(
  data: unknown,
  format: string,
  columns?: TableColumnDef[]
): string {
  switch (format) {
    case "json":
      return JSON.stringify(data, null, 2);
    case "yaml":
      return yamlStringify(data);
    case "table":
    default:
      return formatTable(data, columns);
  }
}

// Auto-detect output format: non-TTY defaults to json for machine consumption
export function resolveOutputFormat(explicit?: string): "json" | "table" | "yaml" {
  if (explicit) return explicit as "json" | "table" | "yaml";
  return process.stdout.isTTY ? "table" : "json";
}

// Format array data as CLI table
function formatTable(data: unknown, columns?: TableColumnDef[]): string {
  if (!data) return chalk.dim("No data");

  // Single object — format as key-value pairs
  if (!Array.isArray(data)) {
    const obj = data as Record<string, unknown>;
    const table = new Table();
    for (const [key, value] of Object.entries(obj)) {
      table.push({ [chalk.bold(key)]: formatValue(value) });
    }
    return table.toString();
  }

  // Empty array
  if (data.length === 0) return chalk.dim("No results");

  // Array — format as rows with column headers
  const items = data as Record<string, unknown>[];
  const cols = columns ?? inferColumns(items[0]);

  const table = new Table({
    head: cols.map((c) => chalk.bold(c.header)),
    ...(cols.some((c) => c.width) ? { colWidths: cols.map((c) => c.width ?? null) } : {}),
  });

  for (const item of items) {
    table.push(cols.map((c) => {
      const val = item[c.key];
      return c.transform ? c.transform(val) : formatValue(val);
    }));
  }

  return table.toString();
}

// Infer columns from first item's keys
function inferColumns(item: Record<string, unknown>): TableColumnDef[] {
  return Object.keys(item)
    .filter((k) => !["created_at", "updated_at", "deleted_at", "org_id"].includes(k))
    .slice(0, 6)
    .map((key) => ({ key, header: key }));
}

// Format a single value for table display
function formatValue(val: unknown): string {
  if (val === null || val === undefined) return chalk.dim("-");
  if (typeof val === "object") return JSON.stringify(val);
  return String(val);
}

// Print output to stdout
export function printOutput(data: unknown, format: string, columns?: TableColumnDef[]): void {
  console.log(formatOutput(data, format, columns));
}
