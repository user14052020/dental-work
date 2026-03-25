import { PaginatedResponse } from "@/shared/types/api";

export type DeliveryItem = {
  id: string;
  created_at: string;
  updated_at: string;
  narad_number: string;
  title: string;
  status: string;
  client_id: string;
  client_name: string;
  delivery_address?: string | null;
  delivery_contact?: string | null;
  delivery_phone?: string | null;
  works_count: number;
  work_numbers: string[];
  work_types: string[];
  executor_names: string[];
  doctor_name?: string | null;
  patient_name?: string | null;
  received_at: string;
  deadline_at?: string | null;
  completed_at?: string | null;
  delivery_sent: boolean;
  delivery_sent_at?: string | null;
  total_price: string;
};

export type DeliveryFilters = {
  page: number;
  page_size: number;
  search?: string;
  client_id?: string;
  executor_id?: string;
  sent?: boolean;
  sort_by?: "client_name" | "deadline_at" | "received_at";
  sort_direction?: "asc" | "desc";
};

export type DeliveryResponse = PaginatedResponse<DeliveryItem>;

export type DeliveryMarkSentPayload = {
  narad_ids: string[];
};

export type DeliveryMarkSentResponse = {
  updated_count: number;
  items: DeliveryItem[];
};
