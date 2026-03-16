import { PaginatedResponse } from "@/shared/types/api";

export const workStatusOptions = [
  { value: "new", label: "Новая" },
  { value: "in_progress", label: "В работе" },
  { value: "in_review", label: "На проверке" },
  { value: "completed", label: "Завершена" },
  { value: "delivered", label: "Выдана" },
  { value: "cancelled", label: "Отменена" }
] as const;

export type WorkStatus = (typeof workStatusOptions)[number]["value"];

export type WorkCompact = {
  id: string;
  created_at: string;
  updated_at: string;
  order_number: string;
  work_type: string;
  status: WorkStatus;
  received_at: string;
  deadline_at?: string | null;
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

export type Work = WorkCompact & {
  client_id: string;
  client_name: string;
  executor_id?: string | null;
  executor_name?: string | null;
  description?: string | null;
  completed_at?: string | null;
  additional_expenses: string;
  labor_hours: string;
  amount_paid: string;
  comment?: string | null;
  materials: WorkMaterialUsage[];
};

export type WorkMaterialUsageInput = {
  material_id: string;
  quantity: string;
};

export type WorkCreatePayload = {
  order_number: string;
  client_id: string;
  executor_id?: string;
  work_type: string;
  description?: string;
  status: WorkStatus;
  received_at: string;
  deadline_at?: string;
  price_for_client: string;
  additional_expenses: string;
  labor_hours: string;
  amount_paid: string;
  comment?: string;
  materials: WorkMaterialUsageInput[];
};

export type WorkUpdateStatusPayload = {
  status: WorkStatus;
  completed_at?: string;
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
