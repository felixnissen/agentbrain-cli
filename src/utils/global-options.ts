import { Command } from "commander";

// Global CLI options available on all commands
export interface GlobalOptions {
  output?: string;
  org?: string;
  apiUrl?: string;
  apiKey?: string;
  verbose?: boolean;
}

export function addGlobalOptions(program: Command): void {
  program
    .option("-o, --output <format>", "Output format: json | table | yaml")
    .option("--org <id>", "Override organization ID")
    .option("--api-url <url>", "Override API base URL")
    .option("--api-key <key>", "Override API key")
    .option("-v, --verbose", "Verbose output");
}

// Extract global options from root command
export function getGlobalOptions(cmd: Command): GlobalOptions {
  const root = cmd.optsWithGlobals();
  return {
    output: root.output,
    org: root.org,
    apiUrl: root.apiUrl,
    apiKey: root.apiKey,
    verbose: root.verbose,
  };
}
