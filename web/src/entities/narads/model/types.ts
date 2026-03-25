import { PaginatedResponse } from "@/shared/types/api";
import { ToothSelectionItem } from "@/entities/works/model/tooth-selection";

export type NaradCompact = {
  id: string;
  created_at: string;
  updated_at: string;
  narad_number: string;
  title: string;
  client_id: string;
  client_name: string;
  client_email?: string | null;
  doctor_id?: string | null;
  doctor_name?: string | null;
  doctor_phone?: string | null;
  contractor_id?: string | null;
  contractor_name?: string | null;
  patient_name?: string | null;
  patient_age?: number | null;
  patient_gender?: string | null;
  require_color_photo: boolean;
  face_shape?: string | null;
  implant_system?: string | null;
  metal_type?: string | null;
  shade_color?: string | null;
  tooth_formula?: string | null;
  status: string;
  received_at: string;
  deadline_at?: string | null;
  completed_at?: string | null;
  closed_at?: string | null;
  is_outside_work: boolean;
  outside_lab_name?: string | null;
  outside_order_number?: string | null;
  outside_cost: string;
  outside_sent_at?: string | null;
  outside_due_at?: string | null;
  outside_returned_at?: string | null;
  outside_comment?: string | null;
  is_closed: boolean;
  works_count: number;
  total_price: string;
  total_cost: string;
  total_margin: string;
  amount_paid: string;
  balance_due: string;
};

export type NaradWork = {
  id: string;
  created_at: string;
  updated_at: string;
  order_number: string;
  work_type: string;
  status: string;
  executor_id?: string | null;
  executor_name?: string | null;
  work_catalog_item_code?: string | null;
  work_catalog_item_name?: string | null;
  price_for_client: string;
  cost_price: string;
  margin: string;
  amount_paid: string;
  balance_due: string;
  received_at: string;
  deadline_at?: string | null;
  completed_at?: string | null;
  closed_at?: string | null;
};

export type NaradStatusLog = {
  id: string;
  created_at: string;
  updated_at: string;
  action: string;
  actor_email?: string | null;
  from_status?: string | null;
  to_status: string;
  note?: string | null;
  details: Record<string, unknown>;
};

export type NaradPayment = {
  id: string;
  created_at: string;
  updated_at: string;
  payment_number: string;
  payment_date: string;
  method: string;
  amount: string;
  amount_allocated_to_narad: string;
  external_reference?: string | null;
  comment?: string | null;
};

export type Narad = NaradCompact & {
  description?: string | null;
  tooth_selection: ToothSelectionItem[];
  works: NaradWork[];
  payments: NaradPayment[];
  status_logs: NaradStatusLog[];
};

export type NaradUpsertPayload = {
  narad_number: string;
  client_id: string;
  doctor_id?: string | null;
  contractor_id?: string | null;
  title: string;
  description?: string | null;
  doctor_name?: string | null;
  doctor_phone?: string | null;
  patient_name?: string | null;
  patient_age?: number | null;
  patient_gender?: string | null;
  require_color_photo?: boolean;
  face_shape?: string | null;
  implant_system?: string | null;
  metal_type?: string | null;
  shade_color?: string | null;
  tooth_formula?: string | null;
  tooth_selection?: ToothSelectionItem[];
  received_at: string;
  deadline_at?: string | null;
  is_outside_work?: boolean;
  outside_lab_name?: string | null;
  outside_order_number?: string | null;
  outside_cost?: string;
  outside_sent_at?: string | null;
  outside_due_at?: string | null;
  outside_returned_at?: string | null;
  outside_comment?: string | null;
};

export type NaradClosePayload = {
  status: "completed" | "delivered" | "cancelled";
  completed_at?: string;
  note?: string;
};

export type NaradReopenPayload = {
  status: "new" | "in_progress" | "in_review";
  note?: string;
};

export type NaradsFilters = {
  page: number;
  page_size: number;
  search?: string;
  status?: string;
  client_id?: string;
  date_from?: string;
  date_to?: string;
};

export type NaradsResponse = PaginatedResponse<NaradCompact>;

export type OutsideWorkItem = {
  narad_id: string;
  narad_number: string;
  title: string;
  client_name: string;
  contractor_id?: string | null;
  contractor_name?: string | null;
  patient_name?: string | null;
  doctor_name?: string | null;
  status: string;
  works_count: number;
  work_numbers: string[];
  work_types: string[];
  outside_lab_name?: string | null;
  outside_order_number?: string | null;
  outside_cost: string;
  outside_sent_at?: string | null;
  outside_due_at?: string | null;
  outside_returned_at?: string | null;
  outside_comment?: string | null;
  outside_status: "sent" | "returned" | "overdue";
  is_outside_overdue: boolean;
  received_at: string;
  deadline_at?: string | null;
};

export type OutsideWorksFilters = {
  page: number;
  page_size: number;
  search?: string;
  client_id?: string;
  state?: string;
};

export type OutsideWorksResponse = PaginatedResponse<OutsideWorkItem>;

export type OutsideWorkMarkSentPayload = {
  contractor_id?: string;
  outside_lab_name?: string;
  outside_order_number?: string;
  outside_cost?: string;
  outside_sent_at: string;
  outside_due_at?: string;
  outside_comment?: string;
};

export type OutsideWorkMarkReturnedPayload = {
  outside_returned_at: string;
  outside_comment?: string;
};
