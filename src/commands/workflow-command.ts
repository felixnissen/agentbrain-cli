import { Command } from "commander";
import { withErrorHandler, fetchAndPrint, createClient, getOutputFormat } from "../utils/command-helpers.js";
import { printOutput } from "../formatters/output-formatter.js";
import { Workflow, WorkflowStep, WorkflowRun } from "../types/api-types.js";

const WORKFLOW_COLUMNS = [
  { key: "id", header: "ID" },
  { key: "name", header: "Name" },
  { key: "enabled", header: "Enabled", transform: (v: unknown) => v ? "yes" : "no" },
  { key: "cron_schedule", header: "Schedule" },
  { key: "status", header: "Status" },
];

const RUN_COLUMNS = [
  { key: "id", header: "Run ID" },
  { key: "status", header: "Status" },
  { key: "started_at", header: "Started" },
  { key: "completed_at", header: "Completed" },
  { key: "triggered_by", header: "Triggered By" },
];

export function registerWorkflowCommand(program: Command): void {
  const wf = program.command("workflow").alias("wf").description("Manage ETL workflows");

  wf
    .command("list")
    .description("List all workflows")
    .action(withErrorHandler(async (cmd) => {
      await fetchAndPrint<Workflow[]>(cmd, (c) => c.get("/workflows"), WORKFLOW_COLUMNS);
    }));

  wf
    .command("get <id>")
    .description("Get workflow details")
    .action(withErrorHandler(async (cmd, id) => {
      await fetchAndPrint<Workflow>(cmd, (c) => c.get(`/workflows/${id}`));
    }));

  wf
    .command("create")
    .description("Create a new workflow")
    .requiredOption("--name <name>", "Workflow name")
    .option("--description <desc>", "Description")
    .option("--cron <schedule>", "Cron schedule expression")
    .action(withErrorHandler(async (cmd) => {
      const opts = cmd.opts();
      await fetchAndPrint<Workflow>(cmd, (c) => c.post("/workflows", {
        name: opts.name,
        description: opts.description,
        cron_schedule: opts.cron,
      }));
    }));

  wf
    .command("update <id>")
    .description("Update a workflow")
    .option("--name <name>", "New name")
    .option("--description <desc>", "New description")
    .option("--cron <schedule>", "New cron schedule")
    .option("--enabled <bool>", "Enable/disable")
    .action(withErrorHandler(async (cmd, id) => {
      const opts = cmd.opts();
      const body: Record<string, unknown> = {};
      if (opts.name) body.name = opts.name;
      if (opts.description) body.description = opts.description;
      if (opts.cron) body.cron_schedule = opts.cron;
      if (opts.enabled !== undefined) body.enabled = opts.enabled === "true";
      await fetchAndPrint<Workflow>(cmd, (c) => c.put(`/workflows/${id}`, body));
    }));

  wf
    .command("delete <id>")
    .description("Delete a workflow")
    .action(withErrorHandler(async (cmd, id) => {
      const { client } = createClient(cmd);
      await client.delete(`/workflows/${id}`);
      console.log("Workflow deleted.");
    }));

  // Steps
  const steps = wf.command("steps").description("Manage workflow steps");

  steps
    .command("list <workflowId>")
    .description("List steps in a workflow")
    .action(withErrorHandler(async (cmd, workflowId) => {
      await fetchAndPrint<WorkflowStep[]>(cmd, (c) => c.get(`/workflows/${workflowId}/steps`));
    }));

  steps
    .command("create <workflowId>")
    .description("Add step to workflow")
    .requiredOption("--operator <type>", "Operator type")
    .option("--config <json>", "Step config as JSON")
    .action(withErrorHandler(async (cmd, workflowId) => {
      const opts = cmd.opts();
      await fetchAndPrint<WorkflowStep>(cmd, (c) => c.post(`/workflows/${workflowId}/steps`, {
        operator_type: opts.operator,
        config: opts.config ? JSON.parse(opts.config) : {},
      }));
    }));

  steps
    .command("update <workflowId> <stepId>")
    .description("Update a workflow step")
    .option("--operator <type>", "New operator type")
    .option("--config <json>", "Updated config as JSON")
    .action(withErrorHandler(async (cmd, workflowId, stepId) => {
      const opts = cmd.opts();
      const body: Record<string, unknown> = {};
      if (opts.operator) body.operator_type = opts.operator;
      if (opts.config) body.config = JSON.parse(opts.config);
      await fetchAndPrint<WorkflowStep>(cmd, (c) => c.put(`/workflows/${workflowId}/steps/${stepId}`, body));
    }));

  steps
    .command("delete <workflowId> <stepId>")
    .description("Delete a workflow step")
    .action(withErrorHandler(async (cmd, workflowId, stepId) => {
      const { client } = createClient(cmd);
      await client.delete(`/workflows/${workflowId}/steps/${stepId}`);
      console.log("Step deleted.");
    }));

  // Run execution
  wf
    .command("run <id>")
    .description("Execute a workflow")
    .action(withErrorHandler(async (cmd, id) => {
      await fetchAndPrint<WorkflowRun>(cmd, (c) => c.post(`/workflows/${id}/run`));
    }));

  wf
    .command("runs <id>")
    .description("List execution history for a workflow")
    .action(withErrorHandler(async (cmd, id) => {
      await fetchAndPrint<WorkflowRun[]>(cmd, (c) => c.get(`/workflows/${id}/runs`), RUN_COLUMNS);
    }));

  wf
    .command("run-detail <runId>")
    .description("Get details of a workflow run")
    .action(withErrorHandler(async (cmd, runId) => {
      await fetchAndPrint<WorkflowRun>(cmd, (c) => c.get(`/workflow-runs/${runId}`));
    }));

  wf
    .command("cancel <runId>")
    .description("Cancel a running workflow")
    .action(withErrorHandler(async (cmd, runId) => {
      await fetchAndPrint(cmd, (c) => c.post(`/workflow-runs/${runId}/cancel`));
    }));

  wf
    .command("run-steps <runId>")
    .description("Get step details of a run")
    .action(withErrorHandler(async (cmd, runId) => {
      await fetchAndPrint(cmd, (c) => c.get(`/workflow-runs/${runId}/steps`));
    }));

  // SSE log streaming
  wf
    .command("logs <runId>")
    .description("Stream real-time logs of a workflow run (SSE)")
    .action(withErrorHandler(async (cmd, runId) => {
      const { client } = createClient(cmd);
      const format = getOutputFormat(cmd);

      console.error("Streaming workflow logs... (Ctrl+C to stop)");

      await client.stream(`/workflow-runs/${runId}/stream`, (data) => {
        if (format === "json") {
          console.log(data);
        } else {
          try {
            const parsed = JSON.parse(data);
            const ts = parsed.timestamp ? `[${parsed.timestamp}] ` : "";
            const level = parsed.level ? `${parsed.level.toUpperCase()} ` : "";
            console.log(`${ts}${level}${parsed.message ?? data}`);
          } catch {
            console.log(data);
          }
        }
      });
    }));
}
