import { Command } from "commander";
import { withErrorHandler, fetchAndPrint, createClient } from "../utils/command-helpers.js";
import { ConnectorSubtype } from "../types/api-types.js";

const SUBTYPE_COLUMNS = [
  { key: "id", header: "ID" },
  { key: "name", header: "Name" },
  { key: "type", header: "Type" },
  { key: "subtype", header: "Subtype" },
  { key: "status", header: "Status" },
];

export function registerConnectorSubtypeCommand(program: Command): void {
  const sub = program.command("connector-subtype").alias("cs").description("Manage connector subtypes");

  sub
    .command("list")
    .description("List all connector subtypes")
    .action(withErrorHandler(async (cmd) => {
      await fetchAndPrint<ConnectorSubtype[]>(cmd, (c) => c.get("/connector-subtypes"), SUBTYPE_COLUMNS);
    }));

  sub
    .command("get <id>")
    .description("Get connector subtype details")
    .action(withErrorHandler(async (cmd, id) => {
      await fetchAndPrint<ConnectorSubtype>(cmd, (c) => c.get(`/connector-subtypes/${id}`));
    }));

  sub
    .command("create")
    .description("Create a connector subtype")
    .requiredOption("--name <name>", "Display name")
    .requiredOption("--type <type>", "Type")
    .requiredOption("--subtype <subtype>", "Subtype key")
    .option("--description <desc>", "Description")
    .option("--config-schema <json>", "Config JSON schema")
    .action(withErrorHandler(async (cmd) => {
      const opts = cmd.opts();
      await fetchAndPrint<ConnectorSubtype>(cmd, (c) => c.post("/connector-subtypes", {
        name: opts.name,
        type: opts.type,
        subtype: opts.subtype,
        description: opts.description,
        config_schema: opts.configSchema ? JSON.parse(opts.configSchema) : undefined,
      }));
    }));

  sub
    .command("delete <id>")
    .description("Delete a connector subtype")
    .action(withErrorHandler(async (cmd, id) => {
      const { client } = createClient(cmd);
      await client.delete(`/connector-subtypes/${id}`);
      console.log("Connector subtype deleted.");
    }));
}
