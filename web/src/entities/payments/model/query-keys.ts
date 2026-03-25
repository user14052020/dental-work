import { PaymentsFilters } from "@/entities/payments/model/types";

export const paymentsQueryKeys = {
  root: ["payments"] as const,
  list: (filters: PaymentsFilters) => [...paymentsQueryKeys.root, "list", filters] as const,
  detail: (paymentId?: string) => [...paymentsQueryKeys.root, "detail", paymentId] as const,
  workCandidates: (clientId?: string, paymentId?: string) =>
    [...paymentsQueryKeys.root, "work-candidates", clientId, paymentId] as const
};
