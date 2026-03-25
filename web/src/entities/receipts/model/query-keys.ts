import { ReceiptFilters } from "@/entities/receipts/model/types";

export const receiptsQueryKeys = {
  root: ["receipts"] as const,
  list: (filters: ReceiptFilters) => [...receiptsQueryKeys.root, "list", filters] as const,
  detail: (receiptId?: string) => [...receiptsQueryKeys.root, "detail", receiptId] as const
};
