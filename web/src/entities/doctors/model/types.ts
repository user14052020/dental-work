import { PaginatedResponse } from "@/shared/types/api";

export type Doctor = {
  id: string;
  created_at: string;
  updated_at: string;
  client_id?: string | null;
  client_name?: string | null;
  full_name: string;
  phone?: string | null;
  email?: string | null;
  specialization?: string | null;
  comment?: string | null;
  is_active: boolean;
};

export type DoctorCreatePayload = {
  client_id?: string;
  full_name: string;
  phone?: string;
  email?: string;
  specialization?: string;
  comment?: string;
  is_active: boolean;
};

export type DoctorUpdatePayload = Partial<DoctorCreatePayload>;

export type DoctorsFilters = {
  page: number;
  page_size: number;
  search?: string;
  active_only?: boolean;
  client_id?: string;
};

export type DoctorsResponse = PaginatedResponse<Doctor>;
