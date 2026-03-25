import { PaginatedResponse } from "@/shared/types/api";

export type Material = {
  id: string;
  created_at: string;
  updated_at: string;
  name: string;
  category?: string | null;
  unit: string;
  stock: string;
  reserved_stock: string;
  available_stock: string;
  purchase_price: string;
  average_price: string;
  supplier?: string | null;
  min_stock: string;
  comment?: string | null;
  is_low_stock: boolean;
};

export type StockMovement = {
  id: string;
  created_at: string;
  updated_at: string;
  movement_type: string;
  quantity_delta: string;
  unit_cost: string;
  total_cost: string;
  balance_after: string;
  receipt_id?: string | null;
  receipt_number?: string | null;
  work_id?: string | null;
  work_order_number?: string | null;
  inventory_adjustment_id?: string | null;
  inventory_adjustment_number?: string | null;
  comment?: string | null;
};

export type MaterialDetail = Material & {
  stock_value: string;
  movements: StockMovement[];
};

export type MaterialCreatePayload = {
  name: string;
  category?: string;
  unit: string;
  stock: string;
  purchase_price: string;
  average_price: string;
  supplier?: string;
  min_stock: string;
  comment?: string;
};

export type MaterialUpdatePayload = Partial<MaterialCreatePayload>;

export type MaterialConsumePayload = {
  quantity: string;
  reason?: string;
};

export type ManualMaterialConsumptionUpdatePayload = {
  quantity: string;
  reason?: string;
};

export type MaterialsFilters = {
  page: number;
  page_size: number;
  search?: string;
  low_stock_only?: boolean;
};

export type MaterialsResponse = PaginatedResponse<Material>;
