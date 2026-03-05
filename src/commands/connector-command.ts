import { Command } from "commander";
import { withErrorHandler, fetchAndPrint, createClient, getOutputFormat } from "../utils/command-helpers.js";
import { printOutput } from "../formatters/output-formatter.js";
import { Connector, ConnectorShare } from "../types/api-types.js";

const CONNECTOR_COLUMNS = [
  { key: "id", header: "ID" },
  { key: "name", header: "Name" },
  { key: "type", header: "Type" },
  { key: "subtype", header: "Subtype" },
  { key: "status", header: "Status" },
];

export function registerConnectorCommand(program: Command): void {
  const conn = program.command("connector").description("Manage data source connectors");

  conn
    .command("list")
    .description("List all connectors")
    .action(withErrorHandler(async (cmd) => {
      await fetchAndPrint<Connector[]>(cmd, (c) => c.get("/connectors"), CONNECTOR_COLUMNS);
    }));

  conn
    .command("my")
    .description("List connectors accessible to me")
    .action(withErrorHandler(async (cmd) => {
      await fetchAndPrint<Connector[]>(cmd, (c) => c.get("/my-connectors"), CONNECTOR_COLUMNS);
    }));

  conn
    .command("get <id>")
    .description("Get connector details")
    .action(withErrorHandler(async (cmd, id) => {
      await fetchAndPrint<Connector>(cmd, (c) => c.get(`/connectors/${id}`));
    }));

  conn
    .command("create")
    .description("Create a new connector")
    .requiredOption("--name <name>", "Connector name")
    .requiredOption("--type <type>", "Connector type (credential|endpoint|secret_key)")
    .requiredOption("--subtype <subtype>", "Connector subtype (postgresql|mysql|mongodb|etc.)")
    .option("--config <json>", "Connector config as JSON string")
    .action(withErrorHandler(async (cmd) => {
      const opts = cmd.opts();
      const config = opts.config ? JSON.parse(opts.config) : {};
      await fetchAndPrint<Connector>(cmd, (c) => c.post("/connectors", {
        name: opts.name,
        type: opts.type,
        subtype: opts.subtype,
        config,
      }));
    }));

  conn
    .command("update <id>")
    .description("Update a connector")
    .option("--name <name>", "New name")
    .option("--config <json>", "Updated config as JSON string")
    .action(withErrorHandler(async (cmd, id) => {
      const opts = cmd.opts();
      const body: Record<string, unknown> = {};
      if (opts.name) body.name = opts.name;
      if (opts.config) body.config = JSON.parse(opts.config);
      await fetchAndPrint<Connector>(cmd, (c) => c.put(`/connectors/${id}`, body));
    }));

  conn
    .command("delete <id>")
    .description("Delete a connector")
    .action(withErrorHandler(async (cmd, id) => {
      const { client } = createClient(cmd);
      await client.delete(`/connectors/${id}`);
      console.log("Connector deleted.");
    }));

  conn
    .command("test <id>")
    .description("Test connector connectivity")
    .action(withErrorHandler(async (cmd, id) => {
      await fetchAndPrint(cmd, (c) => c.post(`/connectors/${id}/test`));
    }));

  conn
    .command("test-config")
    .description("Test config before creating connector")
    .requiredOption("--type <type>", "Connector type")
    .requiredOption("--subtype <subtype>", "Connector subtype")
    .requiredOption("--config <json>", "Config as JSON string")
    .action(withErrorHandler(async (cmd) => {
      const opts = cmd.opts();
      await fetchAndPrint(cmd, (c) => c.post("/connectors/test-config", {
        type: opts.type,
        subtype: opts.subtype,
        config: JSON.parse(opts.config),
      }));
    }));

  conn
    .command("databases <id>")
    .description("List databases in a connector")
    .action(withErrorHandler(async (cmd, id) => {
      await fetchAndPrint(cmd, (c) => c.get(`/connectors/${id}/databases`));
    }));

  conn
    .command("schemas <id>")
    .description("List schemas in a connector")
    .action(withErrorHandler(async (cmd, id) => {
      await fetchAndPrint(cmd, (c) => c.get(`/connectors/${id}/schemas`));
    }));

  conn
    .command("tables <id>")
    .description("List tables in a connector")
    .action(withErrorHandler(async (cmd, id) => {
      await fetchAndPrint(cmd, (c) => c.get(`/connectors/${id}/tables`));
    }));

  conn
    .command("columns <connectorId> <tableName>")
    .description("Get columns for a table")
    .action(withErrorHandler(async (cmd, connectorId, tableName) => {
      await fetchAndPrint(cmd, (c) => c.get(`/connectors/${connectorId}/tables/${tableName}/columns`), [
        { key: "name", header: "Column" },
        { key: "type", header: "Type" },
        { key: "nullable", header: "Nullable" },
      ]);
    }));

  conn
    .command("data <connectorId> <tableName>")
    .description("Preview data from a table")
    .option("--limit <n>", "Row limit", "10")
    .action(withErrorHandler(async (cmd, connectorId, tableName) => {
      const opts = cmd.opts();
      await fetchAndPrint(cmd, (c) => c.get(`/connectors/${connectorId}/tables/${tableName}/data`, {
        limit: opts.limit,
      }));
    }));

  conn
    .command("counts")
    .description("Count total connectors")
    .action(withErrorHandler(async (cmd) => {
      await fetchAndPrint(cmd, (c) => c.get("/connectors/counts"));
    }));

  // Sharing subcommands
  const share = conn.command("share").description("Manage connector sharing");

  share
    .command("list <connectorId>")
    .description("List shares for a connector")
    .action(withErrorHandler(async (cmd, connectorId) => {
      await fetchAndPrint<ConnectorShare[]>(cmd, (c) => c.get(`/connectors/${connectorId}/shares`));
    }));

  share
    .command("create <connectorId>")
    .description("Share connector with a user")
    .requiredOption("--user-id <userId>", "User to share with")
    .option("--permissions <tables>", "Comma-separated table names")
    .action(withErrorHandler(async (cmd, connectorId) => {
      const opts = cmd.opts();
      await fetchAndPrint<ConnectorShare>(cmd, (c) => c.post(`/connectors/${connectorId}/shares`, {
        shared_with_user_id: opts.userId,
        permissions: opts.permissions?.split(","),
      }));
    }));

  share
    .command("delete <connectorId> <shareId>")
    .description("Remove a connector share")
    .action(withErrorHandler(async (cmd, connectorId, shareId) => {
      const { client } = createClient(cmd);
      await client.delete(`/connectors/${connectorId}/shares/${shareId}`);
      console.log("Share removed.");
    }));
}
