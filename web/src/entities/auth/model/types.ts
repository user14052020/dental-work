export type AuthUser = {
  id: string;
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
  created_at: string;
  updated_at: string;
};

export type AuthSession = {
  user: AuthUser;
};

export type LoginPayload = {
  email: string;
  password: string;
};

export type RegisterPayload = LoginPayload;
