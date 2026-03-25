import { PaginatedResponse } from "@/shared/types/api";

export type MaterialReceiptCompact = {
  id: string;
  created_at: string;
  updated_at: string;
  receipt_number: string;
  received_at: string;
  supplier?: string | null;
  items_count: number;
  total_amount: string;
  total_quantity: string;
};

export type MaterialReceiptItem = {
  id: string;
  created_at: string;
  updated_at: string;
  material_id: string;
  material_name: string;
  quantity: string;
  unit_price: string;
  total_price: string;
  sort_order: number;
};

export type MaterialReceipt = MaterialReceiptCompact & {
  comment?: string | null;
  items: MaterialReceiptItem[];
};

export type MaterialReceiptItemInput = {
  material_id: string;
  quantity: string;
  unit_price: string;
};

export type MaterialReceiptCreatePayload = {
  receipt_number: string;
  received_at: string;
  supplier?: string;
  comment?: string;
  items: MaterialReceiptItemInput[];
};

export type ReceiptFilters = {
  page: number;
  page_size: number;
  search?: string;
  supplier?: string;
  date_from?: string;
  date_to?: string;
};

export type MaterialReceiptsResponse = PaginatedResponse<MaterialReceiptCompact>;
