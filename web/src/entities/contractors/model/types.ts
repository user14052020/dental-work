import { PaginatedResponse } from "@/shared/types/api";

export type Contractor = {
  id: string;
  created_at: string;
  updated_at: string;
  name: string;
  contact_person?: string | null;
  phone?: string | null;
  email?: string | null;
  address?: string | null;
  comment?: string | null;
  is_active: boolean;
};

export type ContractorCreatePayload = {
  name: string;
  contact_person?: string;
  phone?: string;
  email?: string;
  address?: string;
  comment?: string;
  is_active: boolean;
};

export type ContractorUpdatePayload = Partial<ContractorCreatePayload>;

export type ContractorsFilters = {
  page: number;
  page_size: number;
  search?: string;
  active_only?: boolean;
};

export type ContractorsResponse = PaginatedResponse<Contractor>;
