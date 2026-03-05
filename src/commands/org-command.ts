import { Command } from "commander";
import { withErrorHandler, fetchAndPrint, createClient } from "../utils/command-helpers.js";
import { setConfigValue } from "../config/config-manager.js";
import { Organization, OrgMember } from "../types/api-types.js";

const ORG_COLUMNS = [
  { key: "id", header: "ID" },
  { key: "name", header: "Name" },
  { key: "slug", header: "Slug" },
  { key: "type", header: "Type" },
  { key: "status", header: "Status" },
];

const MEMBER_COLUMNS = [
  { key: "id", header: "ID" },
  { key: "user_id", header: "User ID" },
  { key: "role", header: "Role" },
  { key: "status", header: "Status" },
  { key: "joined_at", header: "Joined" },
];

export function registerOrgCommand(program: Command): void {
  const org = program.command("org").description("Manage organizations");

  org
    .command("list")
    .description("List all accessible organizations")
    .action(withErrorHandler(async (cmd) => {
      await fetchAndPrint<Organization[]>(cmd, (c) => c.get("/organizations"));
    }));

  org
    .command("me")
    .description("List my organizations")
    .action(withErrorHandler(async (cmd) => {
      await fetchAndPrint<Organization[]>(cmd, (c) => c.get("/organizations/me"), ORG_COLUMNS);
    }));

  org
    .command("get <id>")
    .description("Get organization details")
    .action(withErrorHandler(async (cmd, id) => {
      await fetchAndPrint<Organization>(cmd, (c) => c.get(`/organizations/${id}`));
    }));

  org
    .command("create")
    .description("Create a new organization")
    .requiredOption("--name <name>", "Organization name")
    .option("--description <desc>", "Organization description")
    .option("--type <type>", "Organization type")
    .action(withErrorHandler(async (cmd) => {
      const opts = cmd.opts();
      await fetchAndPrint<Organization>(cmd, (c) => c.post("/organizations", {
        name: opts.name,
        description: opts.description,
        type: opts.type,
      }));
    }));

  org
    .command("update <id>")
    .description("Update an organization")
    .option("--name <name>", "Organization name")
    .option("--description <desc>", "Description")
    .action(withErrorHandler(async (cmd, id) => {
      const opts = cmd.opts();
      await fetchAndPrint<Organization>(cmd, (c) => c.put(`/organizations/${id}`, {
        name: opts.name,
        description: opts.description,
      }));
    }));

  org
    .command("delete <id>")
    .description("Delete an organization")
    .action(withErrorHandler(async (cmd, id) => {
      const { client } = createClient(cmd);
      await client.delete(`/organizations/${id}`);
      console.log("Organization deleted.");
    }));

  org
    .command("members <id>")
    .description("List organization members")
    .action(withErrorHandler(async (cmd, id) => {
      await fetchAndPrint<OrgMember[]>(cmd, (c) => c.get(`/organizations/${id}/members`), MEMBER_COLUMNS);
    }));

  org
    .command("add-member <orgId>")
    .description("Add member to organization")
    .requiredOption("--user-id <userId>", "User ID to add")
    .option("--role <role>", "Member role (admin/member/viewer)", "member")
    .action(withErrorHandler(async (cmd, orgId) => {
      const opts = cmd.opts();
      await fetchAndPrint<OrgMember>(cmd, (c) => c.post(`/organizations/${orgId}/members`, {
        user_id: opts.userId,
        role: opts.role,
      }));
    }));

  org
    .command("switch <id>")
    .description("Switch active organization (saves to config)")
    .action((_id: string) => {
      setConfigValue("orgId", _id);
      console.log(`Switched to organization: ${_id}`);
    });
}
