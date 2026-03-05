import { Command } from "commander";
import { setConfigValue, getConfigValue, listConfig } from "../config/config-manager.js";
import { printOutput } from "../formatters/output-formatter.js";
import { getOutputFormat } from "../utils/command-helpers.js";

export function registerConfigCommand(program: Command): void {
  const config = program.command("config").description("Manage CLI configuration");

  config
    .command("set <key> <value>")
    .description("Set a config value (apiUrl, apiKey, orgId, output, timeout)")
    .action((key: string, value: string) => {
      try {
        setConfigValue(key, value);
        console.log(`Set ${key} successfully.`);
      } catch (err) {
        console.error((err as Error).message);
        process.exit(1);
      }
    });

  config
    .command("get <key>")
    .description("Get a config value")
    .action((key: string) => {
      try {
        const value = getConfigValue(key);
        console.log(value);
      } catch (err) {
        console.error((err as Error).message);
        process.exit(1);
      }
    });

  config
    .command("list")
    .description("List all resolved config values with sources")
    .action(function (this: Command) {
      const format = getOutputFormat(this);
      const items = listConfig();
      printOutput(items, format, [
        { key: "key", header: "Key" },
        { key: "value", header: "Value" },
        { key: "source", header: "Source" },
      ]);
    });
}
