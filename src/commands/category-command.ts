import { Command } from "commander";
import { withErrorHandler, fetchAndPrint, createClient } from "../utils/command-helpers.js";
import { Category } from "../types/api-types.js";

const CATEGORY_COLUMNS = [
  { key: "id", header: "ID" },
  { key: "name", header: "Name" },
  { key: "slug", header: "Slug" },
  { key: "parent_id", header: "Parent" },
  { key: "status", header: "Status" },
];

export function registerCategoryCommand(program: Command): void {
  const cat = program.command("category").alias("cat").description("Manage categories");

  cat
    .command("list")
    .description("List all categories")
    .action(withErrorHandler(async (cmd) => {
      await fetchAndPrint<Category[]>(cmd, (c) => c.get("/categories"), CATEGORY_COLUMNS);
    }));

  cat
    .command("tree")
    .description("Get hierarchical category tree")
    .action(withErrorHandler(async (cmd) => {
      await fetchAndPrint<Category[]>(cmd, (c) => c.get("/categories/tree"));
    }));

  cat
    .command("get <id>")
    .description("Get category details")
    .action(withErrorHandler(async (cmd, id) => {
      await fetchAndPrint<Category>(cmd, (c) => c.get(`/categories/${id}`));
    }));

  cat
    .command("create")
    .description("Create a category")
    .requiredOption("--name <name>", "Category name")
    .option("--parent-id <id>", "Parent category ID")
    .option("--description <desc>", "Description")
    .action(withErrorHandler(async (cmd) => {
      const opts = cmd.opts();
      await fetchAndPrint<Category>(cmd, (c) => c.post("/categories", {
        name: opts.name,
        parent_id: opts.parentId,
        description: opts.description,
      }));
    }));

  cat
    .command("update <id>")
    .description("Update a category")
    .option("--name <name>", "New name")
    .option("--description <desc>", "New description")
    .action(withErrorHandler(async (cmd, id) => {
      const opts = cmd.opts();
      await fetchAndPrint<Category>(cmd, (c) => c.put(`/categories/${id}`, {
        name: opts.name,
        description: opts.description,
      }));
    }));

  cat
    .command("delete <id>")
    .description("Delete a category")
    .action(withErrorHandler(async (cmd, id) => {
      const { client } = createClient(cmd);
      await client.delete(`/categories/${id}`);
      console.log("Category deleted.");
    }));
}
