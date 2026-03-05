import { Command } from "commander";
import { withErrorHandler, fetchAndPrint, createClient } from "../utils/command-helpers.js";
import { Knowledge, KnowledgeVersion, KnowledgeShare } from "../types/api-types.js";

const KB_COLUMNS = [
  { key: "id", header: "ID" },
  { key: "title", header: "Title" },
  { key: "description", header: "Description" },
  { key: "embedding_model", header: "Model" },
  { key: "status", header: "Status" },
];

export function registerKnowledgeCommand(program: Command): void {
  const kb = program.command("knowledge").alias("kb").description("Manage knowledge bases");

  kb
    .command("list")
    .description("List all knowledge bases")
    .action(withErrorHandler(async (cmd) => {
      await fetchAndPrint<Knowledge[]>(cmd, (c) => c.get("/knowledges"), KB_COLUMNS);
    }));

  kb
    .command("get <id>")
    .description("Get knowledge base details")
    .action(withErrorHandler(async (cmd, id) => {
      await fetchAndPrint<Knowledge>(cmd, (c) => c.get(`/knowledges/${id}`));
    }));

  kb
    .command("create")
    .description("Create a new knowledge base")
    .requiredOption("--title <title>", "Knowledge base title")
    .option("--description <desc>", "Description")
    .option("--embedding-model <model>", "Embedding model name")
    .action(withErrorHandler(async (cmd) => {
      const opts = cmd.opts();
      await fetchAndPrint<Knowledge>(cmd, (c) => c.post("/knowledges", {
        title: opts.title,
        description: opts.description,
        embedding_model: opts.embeddingModel,
      }));
    }));

  kb
    .command("update <id>")
    .description("Update a knowledge base")
    .option("--title <title>", "New title")
    .option("--description <desc>", "New description")
    .action(withErrorHandler(async (cmd, id) => {
      const opts = cmd.opts();
      await fetchAndPrint<Knowledge>(cmd, (c) => c.put(`/knowledges/${id}`, {
        title: opts.title,
        description: opts.description,
      }));
    }));

  kb
    .command("delete <id>")
    .description("Delete a knowledge base")
    .action(withErrorHandler(async (cmd, id) => {
      const { client } = createClient(cmd);
      await client.delete(`/knowledges/${id}`);
      console.log("Knowledge base deleted.");
    }));

  // Version history
  kb
    .command("versions <id>")
    .description("List version history")
    .action(withErrorHandler(async (cmd, id) => {
      await fetchAndPrint<KnowledgeVersion[]>(cmd, (c) => c.get(`/knowledges/${id}/versions`), [
        { key: "id", header: "ID" },
        { key: "version_number", header: "Version" },
        { key: "embedding_model", header: "Model" },
        { key: "created_at", header: "Created" },
      ]);
    }));

  kb
    .command("version <knowledgeId> <versionId>")
    .description("Get a specific version")
    .action(withErrorHandler(async (cmd, knowledgeId, versionId) => {
      await fetchAndPrint<KnowledgeVersion>(cmd, (c) => c.get(`/knowledges/${knowledgeId}/versions/${versionId}`));
    }));

  kb
    .command("rollback <knowledgeId> <versionId>")
    .description("Rollback to a specific version")
    .action(withErrorHandler(async (cmd, knowledgeId, versionId) => {
      await fetchAndPrint<Knowledge>(cmd, (c) => c.post(`/knowledges/${knowledgeId}/rollback/${versionId}`));
    }));

  // Sharing
  const share = kb.command("share").description("Manage knowledge base sharing");

  share
    .command("list <knowledgeId>")
    .description("List shares for a knowledge base")
    .action(withErrorHandler(async (cmd, knowledgeId) => {
      await fetchAndPrint<KnowledgeShare[]>(cmd, (c) => c.get(`/knowledges/${knowledgeId}/shares`));
    }));

  share
    .command("create <knowledgeId>")
    .description("Share knowledge base with a user")
    .requiredOption("--user-id <userId>", "User to share with")
    .option("--access-level <level>", "Access level", "read")
    .action(withErrorHandler(async (cmd, knowledgeId) => {
      const opts = cmd.opts();
      await fetchAndPrint<KnowledgeShare>(cmd, (c) => c.post(`/knowledges/${knowledgeId}/shares`, {
        shared_with_user_id: opts.userId,
        access_level: opts.accessLevel,
      }));
    }));

  share
    .command("delete <knowledgeId> <shareId>")
    .description("Remove a knowledge base share")
    .action(withErrorHandler(async (cmd, knowledgeId, shareId) => {
      const { client } = createClient(cmd);
      await client.delete(`/knowledges/${knowledgeId}/shares/${shareId}`);
      console.log("Share removed.");
    }));
}
