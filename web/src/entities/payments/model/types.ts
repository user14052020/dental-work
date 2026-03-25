import { PaginatedResponse } from "@/shared/types/api";

export const paymentMethodOptions = [
  { value: "cash", label: "Наличные" },
  { value: "card", label: "Карта" },
  { value: "bank_transfer", label: "Безналичный перевод" },
  { value: "sbp", label: "СБП" },
  { value: "other", label: "Прочее" }
] as const;

export type PaymentMethod = (typeof paymentMethodOptions)[number]["value"];

export type PaymentAllocation = {
  id: string;
  created_at: string;
  updated_at: string;
  work_id: string;
  narad_id?: string | null;
  narad_number?: string | null;
  narad_title?: string | null;
  work_order_number: string;
  work_type: string;
  work_status: string;
  received_at: string;
  deadline_at?: string | null;
  work_total: string;
  work_amount_paid: string;
  work_balance_due: string;
  amount: string;
};

export type PaymentNaradAllocation = {
  narad_id: string;
  narad_number: string;
  narad_title: string;
  narad_status: string;
  received_at: string;
  deadline_at?: string | null;
  works_count: number;
  total_price: string;
  amount_paid: string;
  balance_due: string;
  amount: string;
};

export type WorkPaymentCandidate = {
  work_id: string;
  order_number: string;
  work_type: string;
  status: string;
  received_at: string;
  deadline_at?: string | null;
  total_price: string;
  amount_paid: string;
  balance_due: string;
  available_to_allocate: string;
  existing_allocation_amount: string;
};

export type NaradPaymentCandidate = {
  narad_id: string;
  narad_number: string;
  title: string;
  status: string;
  received_at: string;
  deadline_at?: string | null;
  works_count: number;
  total_price: string;
  amount_paid: string;
  balance_due: string;
  available_to_allocate: string;
  existing_allocation_amount: string;
};

export type PaymentCompact = {
  id: string;
  created_at: string;
  updated_at: string;
  payment_number: string;
  client_id: string;
  client_name: string;
  payment_date: string;
  method: PaymentMethod;
  amount: string;
  allocated_total: string;
  unallocated_total: string;
  allocation_count: number;
  external_reference?: string | null;
  comment?: string | null;
};

export type Payment = PaymentCompact & {
  allocations: PaymentAllocation[];
  narad_allocations: PaymentNaradAllocation[];
};

export type PaymentAllocationPayload = {
  work_id: string;
  amount: string;
};

export type PaymentNaradAllocationPayload = {
  narad_id: string;
  amount: string;
};

export type PaymentCreatePayload = {
  payment_number?: string;
  client_id: string;
  payment_date: string;
  method: PaymentMethod;
  amount: string;
  external_reference?: string;
  comment?: string;
  allocations?: PaymentAllocationPayload[];
  narad_allocations?: PaymentNaradAllocationPayload[];
};

export type PaymentUpdatePayload = Partial<PaymentCreatePayload>;

export type PaymentReturnNaradAllocationPayload = {
  narad_id: string;
};

export type PaymentsFilters = {
  page: number;
  page_size: number;
  search?: string;
  client_id?: string;
  method?: PaymentMethod;
  date_from?: string;
  date_to?: string;
};

export type PaymentsResponse = PaginatedResponse<PaymentCompact>;
