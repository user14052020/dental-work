import { PaginatedResponse } from "@/shared/types/api";

export const operationExecutionStatusOptions = [
  { value: "planned", label: "Запланирована" },
  { value: "in_progress", label: "В работе" },
  { value: "completed", label: "Завершена" },
  { value: "cancelled", label: "Отменена" }
] as const;

export type OperationExecutionStatus = (typeof operationExecutionStatusOptions)[number]["value"];

export type ExecutorCategory = {
  id: string;
  created_at: string;
  updated_at: string;
  code: string;
  name: string;
  description?: string | null;
  sort_order: number;
  is_active: boolean;
};

export type ExecutorCategoryCreatePayload = {
  code: string;
  name: string;
  description?: string;
  sort_order: number;
  is_active: boolean;
};

export type ExecutorCategoryUpdatePayload = Partial<ExecutorCategoryCreatePayload>;

export type ExecutorCategoriesFilters = {
  page: number;
  page_size: number;
  search?: string;
  active_only?: boolean;
};

export type ExecutorCategoriesResponse = PaginatedResponse<ExecutorCategory>;

export type OperationCategoryRate = {
  id: string;
  created_at: string;
  updated_at: string;
  executor_category_id: string;
  executor_category_code: string;
  executor_category_name: string;
  labor_rate: string;
};

export type OperationCategoryRatePayload = {
  executor_category_id: string;
  labor_rate: string;
};

export type OperationCatalog = {
  id: string;
  created_at: string;
  updated_at: string;
  code: string;
  name: string;
  operation_group?: string | null;
  description?: string | null;
  default_quantity: string;
  default_duration_hours: string;
  is_active: boolean;
  sort_order: number;
  rates: OperationCategoryRate[];
};

export type OperationCatalogCreatePayload = {
  code: string;
  name: string;
  operation_group?: string;
  description?: string;
  default_quantity: string;
  default_duration_hours: string;
  is_active: boolean;
  sort_order: number;
  rates: OperationCategoryRatePayload[];
};

export type OperationCatalogUpdatePayload = Partial<OperationCatalogCreatePayload>;

export type OperationsFilters = {
  page: number;
  page_size: number;
  search?: string;
  active_only?: boolean;
};

export type OperationsResponse = PaginatedResponse<OperationCatalog>;

export type WorkOperationCreatePayload = {
  operation_id: string;
  executor_id?: string;
  quantity: string;
  unit_labor_cost_override?: string;
  note?: string;
};

export type WorkOperationStatusUpdatePayload = {
  status: OperationExecutionStatus;
};
