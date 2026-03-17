import { PaginatedResponse } from "@/shared/types/api";

export type Executor = {
  id: string;
  created_at: string;
  updated_at: string;
  full_name: string;
  phone?: string | null;
  email?: string | null;
  specialization?: string | null;
  payment_category_id?: string | null;
  payment_category_name?: string | null;
  hourly_rate: string;
  comment?: string | null;
  is_active: boolean;
  work_count: number;
  production_total: string;
  earnings_total: string;
  earnings_current_month: string;
};

export type ExecutorCreatePayload = {
  full_name: string;
  phone?: string;
  email?: string;
  specialization?: string;
  payment_category_id?: string | null;
  hourly_rate: string;
  comment?: string;
  is_active: boolean;
};

export type ExecutorUpdatePayload = Partial<ExecutorCreatePayload>;

export type ExecutorsFilters = {
  page: number;
  page_size: number;
  search?: string;
  active_only?: boolean;
};

export type ExecutorsResponse = PaginatedResponse<Executor>;
