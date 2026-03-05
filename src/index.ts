import { Command } from "commander";
import { addGlobalOptions } from "./utils/global-options.js";
import { registerConfigCommand } from "./commands/config-command.js";
import { registerOrgCommand } from "./commands/org-command.js";
import { registerConnectorCommand } from "./commands/connector-command.js";
import { registerConnectorSubtypeCommand } from "./commands/connector-subtype-command.js";
import { registerKnowledgeCommand } from "./commands/knowledge-command.js";
import { registerWorkflowCommand } from "./commands/workflow-command.js";
import { registerSearchCommand } from "./commands/search-command.js";
import { registerQueryLogCommand } from "./commands/query-log-command.js";
import { registerPermissionCommand } from "./commands/permission-command.js";
import { registerCategoryCommand } from "./commands/category-command.js";
import { registerTagCommand } from "./commands/tag-command.js";

const program = new Command();

program
  .name("agentbrain")
  .description("CLI for AgentBrain enterprise data hub — manage organizations, connectors, knowledge bases, workflows, and more")
  .version("0.1.0");

// Register global options (--output, --org, --api-url, --api-key, --verbose)
addGlobalOptions(program);

// Register all command groups
registerConfigCommand(program);
registerOrgCommand(program);
registerConnectorCommand(program);
registerConnectorSubtypeCommand(program);
registerKnowledgeCommand(program);
registerWorkflowCommand(program);
registerSearchCommand(program);
registerQueryLogCommand(program);
registerPermissionCommand(program);
registerCategoryCommand(program);
registerTagCommand(program);

program.parse();
