import { PaginatedResponse } from "@/shared/types/api";

export type Material = {
  id: string;
  created_at: string;
  updated_at: string;
  name: string;
  category?: string | null;
  unit: string;
  stock: string;
  purchase_price: string;
  average_price: string;
  supplier?: string | null;
  min_stock: string;
  comment?: string | null;
  is_low_stock: boolean;
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
};

export type MaterialsFilters = {
  page: number;
  page_size: number;
  search?: string;
  low_stock_only?: boolean;
};

export type MaterialsResponse = PaginatedResponse<Material>;
