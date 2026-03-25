import {
  OperationExecutionStatus,
  WorkOperationCreatePayload
} from "@/entities/operations/model/types";
import { PaymentMethod } from "@/entities/payments/model/types";
import { PaginatedResponse } from "@/shared/types/api";

export const workStatusOptions = [
  { value: "new", label: "Новая" },
  { value: "in_progress", label: "В работе" },
  { value: "in_review", label: "На проверке" },
  { value: "completed", label: "Завершена" },
  { value: "delivered", label: "Выдана" },
  { value: "cancelled", label: "Отменена" }
] as const;

export const patientGenderOptions = [
  { value: "male", label: "Мужской" },
  { value: "female", label: "Женский" }
] as const;

export const faceShapeOptions = [
  { value: "square", label: "Квадратная" },
  { value: "oval", label: "Овальная" },
  { value: "triangle", label: "Треугольная" }
] as const;

export type WorkStatus = (typeof workStatusOptions)[number]["value"];

export type WorkCompact = {
  id: string;
  created_at: string;
  updated_at: string;
  narad_id: string;
  narad_number: string;
  order_number: string;
  work_type: string;
  work_catalog_item_id?: string | null;
  status: WorkStatus;
  received_at: string;
  deadline_at?: string | null;
  delivery_sent: boolean;
  delivery_sent_at?: string | null;
  is_closed: boolean;
  price_for_client: string;
  cost_price: string;
  margin: string;
};

export type WorkMaterialUsage = {
  id: string;
  created_at: string;
  updated_at: string;
  material_id: string;
  material_name: string;
  quantity: string;
  unit_cost: string;
  total_cost: string;
};

export type WorkItem = {
  id: string;
  created_at: string;
  updated_at: string;
  work_catalog_item_id?: string | null;
  work_catalog_item_code?: string | null;
  work_catalog_item_name?: string | null;
  work_catalog_item_category?: string | null;
  work_type: string;
  description?: string | null;
  quantity: string;
  unit_price: string;
  total_price: string;
  sort_order: number;
};

export type WorkAttachment = {
  id: string;
  created_at: string;
  updated_at: string;
  file_name: string;
  content_type: string;
  file_size: number;
  uploaded_by_email?: string | null;
  download_url: string;
};

export type WorkPaymentAllocation = {
  id: string;
  created_at: string;
  updated_at: string;
  payment_id: string;
  payment_number: string;
  payment_date: string;
  payment_method: PaymentMethod;
  payment_amount: string;
  allocated_amount: string;
  payment_unallocated_total: string;
  external_reference?: string | null;
};

export type WorkOperationLog = {
  id: string;
  created_at: string;
  updated_at: string;
  action: string;
  actor_email?: string | null;
  details: Record<string, unknown>;
};

export type WorkOperation = {
  id: string;
  created_at: string;
  updated_at: string;
  operation_id?: string | null;
  operation_code?: string | null;
  operation_name: string;
  executor_id?: string | null;
  executor_name?: string | null;
  executor_category_id?: string | null;
  executor_category_name?: string | null;
  quantity: string;
  unit_labor_cost: string;
  total_labor_cost: string;
  status: OperationExecutionStatus;
  sort_order: number;
  manual_rate_override: boolean;
  note?: string | null;
  logs: WorkOperationLog[];
};

export type Work = WorkCompact & {
  executor_id?: string | null;
  executor_name?: string | null;
  work_catalog_item_code?: string | null;
  work_catalog_item_name?: string | null;
  work_catalog_item_category?: string | null;
  description?: string | null;
  completed_at?: string | null;
  closed_at?: string | null;
  base_price_for_client: string;
  price_adjustment_percent: string;
  additional_expenses: string;
  labor_hours: string;
  labor_cost: string;
  amount_paid: string;
  balance_due: string;
  work_items: WorkItem[];
  attachments: WorkAttachment[];
  payment_allocations: WorkPaymentAllocation[];
  operations: WorkOperation[];
  materials: WorkMaterialUsage[];
  change_logs: WorkChangeLog[];
};

export type WorkChangeLog = {
  id: string;
  created_at: string;
  updated_at: string;
  action: string;
  actor_email?: string | null;
  details: Record<string, unknown>;
};

export type WorkMaterialUsageInput = {
  material_id: string;
  quantity: string;
};

export type WorkCreatePayload = {
  narad_id: string;
  executor_id: string;
  work_catalog_item_id: string;
  description?: string;
  status: WorkStatus;
  received_at: string;
  deadline_at?: string;
  base_price_for_client?: string;
  price_adjustment_percent?: string;
  price_for_client: string;
  additional_expenses: string;
  labor_hours: string;
  work_items?: WorkItemInput[];
  operations: WorkOperationCreatePayload[];
  materials: WorkMaterialUsageInput[];
};

export type WorkItemInput = {
  work_catalog_item_id?: string;
  description?: string;
  quantity: string;
  unit_price?: string;
};

export type WorkUpdateStatusPayload = {
  status: WorkStatus;
  completed_at?: string;
};

export type WorkClosePayload = {
  status: WorkStatus;
  completed_at?: string;
  note?: string;
};

export type WorkReopenPayload = {
  status: WorkStatus;
  note?: string;
};

export type WorksFilters = {
  page: number;
  page_size: number;
  search?: string;
  status?: string;
  client_id?: string;
  executor_id?: string;
  date_from?: string;
  date_to?: string;
};

export type WorksResponse = PaginatedResponse<WorkCompact>;
