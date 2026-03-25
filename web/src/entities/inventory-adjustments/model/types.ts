import { PaginatedResponse } from "@/shared/types/api";

export type InventoryAdjustmentCompact = {
  id: string;
  created_at: string;
  updated_at: string;
  adjustment_number: string;
  recorded_at: string;
  items_count: number;
  changed_items_count: number;
  positive_delta_total: string;
  negative_delta_total: string;
  total_cost_impact: string;
};

export type InventoryAdjustmentItem = {
  id: string;
  created_at: string;
  updated_at: string;
  material_id: string;
  material_name: string;
  unit: string;
  expected_stock: string;
  actual_stock: string;
  quantity_delta: string;
  unit_cost: string;
  total_cost: string;
  sort_order: number;
  comment?: string | null;
};

export type InventoryAdjustment = InventoryAdjustmentCompact & {
  comment?: string | null;
  items: InventoryAdjustmentItem[];
};

export type InventoryAdjustmentItemInput = {
  material_id: string;
  actual_stock: string;
  comment?: string;
};

export type InventoryAdjustmentCreatePayload = {
  adjustment_number: string;
  recorded_at: string;
  comment?: string;
  items: InventoryAdjustmentItemInput[];
};

export type InventoryAdjustmentFilters = {
  page: number;
  page_size: number;
  search?: string;
  date_from?: string;
  date_to?: string;
};

export type InventoryAdjustmentsResponse = PaginatedResponse<InventoryAdjustmentCompact>;
