// Standard API response envelope from AgentBrain backend
export interface ApiResponse<T> {
  data: T;
  message?: string;
  error?: string;
}

// Paginated list response
export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
}

// Common entity fields
export interface BaseEntity {
  id: string;
  created_at: string;
  updated_at: string;
}

// Organization
export interface Organization extends BaseEntity {
  name: string;
  slug: string;
  description?: string;
  logo_url?: string;
  type?: string;
  employee_size?: string;
  status: string;
  created_by: string;
}

export interface OrgMember extends BaseEntity {
  org_id: string;
  user_id: string;
  role: "owner" | "admin" | "member" | "viewer";
  status: string;
  invited_by?: string;
  joined_at?: string;
}

// Connector
export interface Connector extends BaseEntity {
  org_id: string;
  name: string;
  slug: string;
  type: string;
  subtype: string;
  metadata?: Record<string, unknown>;
  visibility?: string;
  status: string;
  created_by: string;
}

export interface ConnectorSubtype extends BaseEntity {
  org_id?: string;
  type: string;
  subtype: string;
  name: string;
  description?: string;
  icon?: string;
  config_schema?: Record<string, unknown>;
  status: string;
  sort_order?: number;
}

export interface TableColumn {
  name: string;
  type: string;
  nullable?: boolean;
  default_value?: string;
}

// Knowledge Base
export interface Knowledge extends BaseEntity {
  org_id: string;
  title: string;
  description?: string;
  embedding_model?: string;
  status: string;
}

export interface KnowledgeVersion extends BaseEntity {
  knowledge_id: string;
  version_number: number;
  content: string;
  embedding_model?: string;
}

export interface KnowledgeShare extends BaseEntity {
  knowledge_id: string;
  shared_with_user_id: string;
  access_level: string;
}

// Workflow
export interface Workflow extends BaseEntity {
  org_id: string;
  name: string;
  description?: string;
  canvas?: Record<string, unknown>;
  cron_schedule?: string;
  enabled: boolean;
  status: string;
  created_by: string;
}

export interface WorkflowStep extends BaseEntity {
  workflow_id: string;
  operator_type: string;
  config?: Record<string, unknown>;
  position?: Record<string, unknown>;
}

export interface WorkflowRun extends BaseEntity {
  workflow_id: string;
  status: "pending" | "running" | "success" | "failed";
  started_at?: string;
  completed_at?: string;
  result?: Record<string, unknown>;
  error_message?: string;
  triggered_by?: string;
}

// Category
export interface Category extends BaseEntity {
  org_id: string;
  parent_id?: string;
  name: string;
  slug: string;
  description?: string;
  icon?: string;
  sort_order?: number;
  status: string;
  children?: Category[];
}

// Tag
export interface Tag extends BaseEntity {
  org_id: string;
  name: string;
  slug: string;
  color?: string;
  status: string;
}

// Permission Group
export interface PermissionGroup extends BaseEntity {
  org_id: string;
  name: string;
  description?: string;
  status: string;
}

// Query Log
export interface QueryLog extends BaseEntity {
  org_id: string;
  executed_by: string;
  query_text: string;
  connector_id?: string;
  execution_time_ms?: number;
  status: "success" | "failed";
  error_message?: string;
}

// Connector Share
export interface ConnectorShare extends BaseEntity {
  connector_id: string;
  shared_with_user_id: string;
  permissions?: string[];
}

export interface ShareTablePermission extends BaseEntity {
  share_id: string;
  table_name: string;
}
