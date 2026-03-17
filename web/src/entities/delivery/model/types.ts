import { PaginatedResponse } from "@/shared/types/api";

export type DeliveryItem = {
  id: string;
  created_at: string;
  updated_at: string;
  order_number: string;
  work_type: string;
  status: string;
  client_id: string;
  client_name: string;
  delivery_address?: string | null;
  delivery_contact?: string | null;
  delivery_phone?: string | null;
  executor_id?: string | null;
  executor_name?: string | null;
  doctor_name?: string | null;
  patient_name?: string | null;
  received_at: string;
  deadline_at?: string | null;
  completed_at?: string | null;
  delivery_sent: boolean;
  delivery_sent_at?: string | null;
  price_for_client: string;
};

export type DeliveryFilters = {
  page: number;
  page_size: number;
  search?: string;
  client_id?: string;
  executor_id?: string;
  sent?: boolean;
};

export type DeliveryResponse = PaginatedResponse<DeliveryItem>;

export type DeliveryMarkSentPayload = {
  work_ids: string[];
};

export type DeliveryMarkSentResponse = {
  updated_count: number;
  items: DeliveryItem[];
};
