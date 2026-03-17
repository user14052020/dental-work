import { PaginatedResponse } from "@/shared/types/api";

export type WorkCatalogTemplateOperation = {
  id: string;
  created_at: string;
  updated_at: string;
  operation_id: string;
  operation_code: string;
  operation_name: string;
  quantity: string;
  note?: string | null;
  sort_order: number;
};

export type WorkCatalogTemplateOperationPayload = {
  operation_id: string;
  quantity: string;
  note?: string;
  sort_order: number;
};

export type WorkCatalogItem = {
  id: string;
  created_at: string;
  updated_at: string;
  code: string;
  name: string;
  category?: string | null;
  description?: string | null;
  base_price: string;
  default_duration_hours: string;
  is_active: boolean;
  sort_order: number;
  default_operations: WorkCatalogTemplateOperation[];
};

export type WorkCatalogItemCreatePayload = {
  code: string;
  name: string;
  category?: string;
  description?: string;
  base_price: string;
  default_duration_hours: string;
  is_active: boolean;
  sort_order: number;
  default_operations: WorkCatalogTemplateOperationPayload[];
};

export type WorkCatalogItemUpdatePayload = Partial<WorkCatalogItemCreatePayload>;

export type WorkCatalogFilters = {
  page: number;
  page_size: number;
  search?: string;
  active_only?: boolean;
  category?: string;
};

export type WorkCatalogResponse = PaginatedResponse<WorkCatalogItem>;
