import { useQuery } from "@tanstack/react-query";

import { fetchReceipt, fetchReceipts } from "@/entities/receipts/api/receipts-api";
import { receiptsQueryKeys } from "@/entities/receipts/model/query-keys";
import { ReceiptFilters } from "@/entities/receipts/model/types";

export function useReceiptsQuery(filters: ReceiptFilters) {
  return useQuery({
    queryKey: receiptsQueryKeys.list(filters),
    queryFn: () => fetchReceipts(filters)
  });
}

export function useReceiptDetailQuery(receiptId?: string) {
  return useQuery({
    queryKey: receiptsQueryKeys.detail(receiptId),
    queryFn: () => fetchReceipt(receiptId as string),
    enabled: Boolean(receiptId)
  });
}
