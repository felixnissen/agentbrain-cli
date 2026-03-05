import { Command } from "commander";
import { withErrorHandler, fetchAndPrint, createClient } from "../utils/command-helpers.js";
import { PermissionGroup } from "../types/api-types.js";

const GROUP_COLUMNS = [
  { key: "id", header: "ID" },
  { key: "name", header: "Name" },
  { key: "description", header: "Description" },
  { key: "status", header: "Status" },
];

export function registerPermissionCommand(program: Command): void {
  const perm = program.command("permission-group").alias("pg").description("Manage permission groups");

  perm
    .command("list")
    .description("List permission groups")
    .action(withErrorHandler(async (cmd) => {
      await fetchAndPrint<PermissionGroup[]>(cmd, (c) => c.get("/permission-groups"), GROUP_COLUMNS);
    }));

  perm
    .command("get <id>")
    .description("Get permission group details")
    .action(withErrorHandler(async (cmd, id) => {
      await fetchAndPrint<PermissionGroup>(cmd, (c) => c.get(`/permission-groups/${id}`));
    }));

  perm
    .command("create")
    .description("Create a permission group")
    .requiredOption("--name <name>", "Group name")
    .option("--description <desc>", "Description")
    .action(withErrorHandler(async (cmd) => {
      const opts = cmd.opts();
      await fetchAndPrint<PermissionGroup>(cmd, (c) => c.post("/permission-groups", {
        name: opts.name,
        description: opts.description,
      }));
    }));

  perm
    .command("update <id>")
    .description("Update a permission group")
    .option("--name <name>", "New name")
    .option("--description <desc>", "New description")
    .action(withErrorHandler(async (cmd, id) => {
      const opts = cmd.opts();
      await fetchAndPrint<PermissionGroup>(cmd, (c) => c.put(`/permission-groups/${id}`, {
        name: opts.name,
        description: opts.description,
      }));
    }));

  perm
    .command("delete <id>")
    .description("Delete a permission group")
    .action(withErrorHandler(async (cmd, id) => {
      const { client } = createClient(cmd);
      await client.delete(`/permission-groups/${id}`);
      console.log("Permission group deleted.");
    }));

  perm
    .command("users <id>")
    .description("List users in a permission group")
    .action(withErrorHandler(async (cmd, id) => {
      await fetchAndPrint(cmd, (c) => c.get(`/permission-groups/${id}/users`));
    }));

  // Permission rules
  perm
    .command("rules <groupId>")
    .description("List permission rules for a group")
    .action(withErrorHandler(async (cmd, groupId) => {
      await fetchAndPrint(cmd, (c) => c.get(`/permission-groups/${groupId}/permissions`));
    }));

  // Verify permission
  program
    .command("verify-permission")
    .description("Verify if current user has a specific permission")
    .requiredOption("--resource-type <type>", "Resource type")
    .option("--resource-id <id>", "Resource ID")
    .requiredOption("--action <action>", "Action to check")
    .action(withErrorHandler(async (cmd) => {
      const opts = cmd.opts();
      await fetchAndPrint(cmd, (c) => c.post("/permissions/verify", {
        resource_type: opts.resourceType,
        resource_id: opts.resourceId,
        action: opts.action,
      }));
    }));
}
