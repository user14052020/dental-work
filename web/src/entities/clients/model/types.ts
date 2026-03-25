import { PaginatedResponse } from "@/shared/types/api";

import { PaymentCompact } from "@/entities/payments/model/types";
import { WorkCompact } from "@/entities/works/model/types";

export type ClientWorkCatalogPrice = {
  id: string;
  created_at: string;
  updated_at: string;
  work_catalog_item_id: string;
  work_catalog_item_code: string;
  work_catalog_item_name: string;
  work_catalog_item_category?: string | null;
  price: string;
  comment?: string | null;
};

export type Client = {
  id: string;
  created_at: string;
  updated_at: string;
  name: string;
  legal_name?: string | null;
  contact_person?: string | null;
  phone?: string | null;
  email?: string | null;
  address?: string | null;
  delivery_address?: string | null;
  delivery_contact?: string | null;
  delivery_phone?: string | null;
  legal_address?: string | null;
  inn?: string | null;
  kpp?: string | null;
  ogrn?: string | null;
  bank_name?: string | null;
  bik?: string | null;
  settlement_account?: string | null;
  correspondent_account?: string | null;
  contract_number?: string | null;
  contract_date?: string | null;
  signer_name?: string | null;
  default_price_adjustment_percent: string;
  comment?: string | null;
  work_count: number;
  order_total: string;
  paid_total: string;
  unpaid_total: string;
};

export type ClientDetail = Client & {
  recent_works: WorkCompact[];
  recent_payments: PaymentCompact[];
  work_catalog_prices: ClientWorkCatalogPrice[];
};

export type ClientWorkCatalogPricePayload = {
  work_catalog_item_id: string;
  price: string;
  comment?: string;
};

export type ClientCreatePayload = {
  name: string;
  legal_name?: string;
  contact_person?: string;
  phone?: string;
  email?: string;
  address?: string;
  delivery_address?: string;
  delivery_contact?: string;
  delivery_phone?: string;
  legal_address?: string;
  inn?: string;
  kpp?: string;
  ogrn?: string;
  bank_name?: string;
  bik?: string;
  settlement_account?: string;
  correspondent_account?: string;
  contract_number?: string;
  contract_date?: string;
  signer_name?: string;
  default_price_adjustment_percent?: string;
  comment?: string;
  work_catalog_prices?: ClientWorkCatalogPricePayload[];
};

export type ClientUpdatePayload = Partial<ClientCreatePayload>;

export type ClientsFilters = {
  page: number;
  page_size: number;
  search?: string;
};

export type ClientsResponse = PaginatedResponse<Client>;
