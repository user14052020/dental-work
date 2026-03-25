import { useQuery } from "@tanstack/react-query";

import {
  fetchPayment,
  fetchPaymentNaradCandidates,
  fetchPayments,
  fetchPaymentWorkCandidates
} from "@/entities/payments/api/payments-api";
import { paymentsQueryKeys } from "@/entities/payments/model/query-keys";
import { PaymentsFilters } from "@/entities/payments/model/types";

export function usePaymentsQuery(filters: PaymentsFilters) {
  return useQuery({
    queryKey: paymentsQueryKeys.list(filters),
    queryFn: () => fetchPayments(filters)
  });
}

export function usePaymentDetailQuery(paymentId?: string) {
  return useQuery({
    queryKey: paymentsQueryKeys.detail(paymentId),
    queryFn: () => fetchPayment(paymentId as string),
    enabled: Boolean(paymentId)
  });
}

export function usePaymentWorkCandidatesQuery(clientId?: string, paymentId?: string) {
  return useQuery({
    queryKey: paymentsQueryKeys.workCandidates(clientId, paymentId),
    queryFn: () => fetchPaymentWorkCandidates(clientId as string, paymentId),
    enabled: Boolean(clientId)
  });
}

export function usePaymentNaradCandidatesQuery(clientId?: string, paymentId?: string) {
  return useQuery({
    queryKey: [...paymentsQueryKeys.workCandidates(clientId, paymentId), "narads"],
    queryFn: () => fetchPaymentNaradCandidates(clientId as string, paymentId),
    enabled: Boolean(clientId)
  });
}
