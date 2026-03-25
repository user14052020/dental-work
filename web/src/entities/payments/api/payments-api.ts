import {
  NaradPaymentCandidate,
  Payment,
  PaymentCreatePayload,
  PaymentReturnNaradAllocationPayload,
  PaymentUpdatePayload,
  PaymentsFilters,
  PaymentsResponse,
  WorkPaymentCandidate
} from "@/entities/payments/model/types";
import { httpClient } from "@/shared/api/http-client";

export function fetchPayments(filters: PaymentsFilters) {
  return httpClient<PaymentsResponse>({
    path: "/api/proxy/payments",
    query: filters
  });
}

export function fetchPayment(paymentId: string) {
  return httpClient<Payment>({
    path: `/api/proxy/payments/${paymentId}`
  });
}

export function fetchPaymentWorkCandidates(clientId: string, paymentId?: string) {
  return httpClient<WorkPaymentCandidate[]>({
    path: "/api/proxy/payments/work-candidates",
    query: {
      client_id: clientId,
      payment_id: paymentId
    }
  });
}

export function fetchPaymentNaradCandidates(clientId: string, paymentId?: string) {
  return httpClient<NaradPaymentCandidate[]>({
    path: "/api/proxy/payments/narad-candidates",
    query: {
      client_id: clientId,
      payment_id: paymentId
    }
  });
}

export function createPayment(payload: PaymentCreatePayload) {
  return httpClient<Payment>({
    path: "/api/proxy/payments",
    method: "POST",
    body: payload
  });
}

export function updatePayment(paymentId: string, payload: PaymentUpdatePayload) {
  return httpClient<Payment>({
    path: `/api/proxy/payments/${paymentId}`,
    method: "PATCH",
    body: payload
  });
}

export function deletePayment(paymentId: string) {
  return httpClient<void>({
    path: `/api/proxy/payments/${paymentId}`,
    method: "DELETE"
  });
}

export function returnPaymentNaradAllocation(paymentId: string, payload: PaymentReturnNaradAllocationPayload) {
  return httpClient<Payment>({
    path: `/api/proxy/payments/${paymentId}/return-narad-allocation`,
    method: "POST",
    body: payload
  });
}

export function deletePaymentUnallocatedBalance(paymentId: string) {
  return httpClient<Payment>({
    path: `/api/proxy/payments/${paymentId}/delete-unallocated-balance`,
    method: "POST"
  });
}
