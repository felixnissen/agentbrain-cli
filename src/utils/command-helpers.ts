import { Command } from "commander";
import { getConfig } from "../config/config-manager.js";
import { AgentBrainConfig } from "../config/config-schema.js";
import { ApiClient } from "../client/http-client.js";
import { ApiError, formatApiError } from "../client/api-error.js";
import { resolveOutputFormat, printOutput, TableColumnDef } from "../formatters/output-formatter.js";
import { getGlobalOptions } from "./global-options.js";

// Create ApiClient from resolved config + CLI overrides
export function createClient(cmd: Command): { client: ApiClient; config: AgentBrainConfig } {
  const opts = getGlobalOptions(cmd);
  const config = getConfig({
    apiUrl: opts.apiUrl,
    apiKey: opts.apiKey,
    orgId: opts.org,
  });
  const client = new ApiClient(config, opts.verbose);
  return { client, config };
}

// Get resolved output format for a command
export function getOutputFormat(cmd: Command): string {
  const opts = getGlobalOptions(cmd);
  const config = getConfig();
  return resolveOutputFormat(opts.output ?? config.output);
}

// Wrap action handler with error handling and output formatting
export function withErrorHandler(
  fn: (cmd: Command, ...args: unknown[]) => Promise<void>
): (...args: unknown[]) => Promise<void> {
  return async (...args: unknown[]) => {
    try {
      // Commander passes the Command as last arg for action handlers
      const cmd = args[args.length - 1] as Command;
      await fn(cmd, ...args.slice(0, -1));
    } catch (err) {
      if (err instanceof ApiError) {
        console.error(formatApiError(err));
      } else if (err instanceof Error) {
        console.error(`Error: ${err.message}`);
      } else {
        console.error("An unexpected error occurred");
      }
      process.exit(1);
    }
  };
}

// Shorthand: fetch data, format, print
export async function fetchAndPrint<T>(
  cmd: Command,
  fetcher: (client: ApiClient) => Promise<T>,
  columns?: TableColumnDef[]
): Promise<void> {
  const { client } = createClient(cmd);
  const format = getOutputFormat(cmd);
  const data = await fetcher(client);
  printOutput(data, format, columns);
}
