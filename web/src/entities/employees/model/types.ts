import { PaginatedResponse } from "@/shared/types/api";

export type Employee = {
  id: string;
  created_at: string;
  updated_at: string;
  full_name: string;
  email: string;
  phone?: string | null;
  job_title?: string | null;
  is_active: boolean;
  is_fired: boolean;
  permission_codes: string[];
  executor_id?: string | null;
  executor_name?: string | null;
  is_technician: boolean;
};

export type EmployeeCreatePayload = {
  full_name: string;
  email: string;
  password: string;
  phone?: string;
  job_title?: string;
  is_active: boolean;
  is_fired: boolean;
  executor_id?: string | null;
  permission_codes?: string[];
};

export type EmployeeUpdatePayload = Partial<EmployeeCreatePayload>;

export type EmployeesFilters = {
  page: number;
  page_size: number;
  search?: string;
  include_fired?: boolean;
};

export type EmployeesResponse = PaginatedResponse<Employee>;
