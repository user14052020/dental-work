import { PaginatedResponse } from "@/shared/types/api";

import { WorkCompact } from "@/entities/works/model/types";

export type Client = {
  id: string;
  created_at: string;
  updated_at: string;
  name: string;
  contact_person?: string | null;
  phone?: string | null;
  email?: string | null;
  address?: string | null;
  comment?: string | null;
  work_count: number;
  order_total: string;
  paid_total: string;
  unpaid_total: string;
};

export type ClientDetail = Client & {
  recent_works: WorkCompact[];
};

export type ClientCreatePayload = {
  name: string;
  contact_person?: string;
  phone?: string;
  email?: string;
  address?: string;
  comment?: string;
};

export type ClientUpdatePayload = Partial<ClientCreatePayload>;

export type ClientsFilters = {
  page: number;
  page_size: number;
  search?: string;
};

export type ClientsResponse = PaginatedResponse<Client>;
