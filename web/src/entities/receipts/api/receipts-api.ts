import {
  MaterialReceipt,
  MaterialReceiptCreatePayload,
  MaterialReceiptsResponse,
  ReceiptFilters
} from "@/entities/receipts/model/types";
import { httpClient } from "@/shared/api/http-client";

export function fetchReceipts(filters: ReceiptFilters) {
  return httpClient<MaterialReceiptsResponse>({
    path: "/api/proxy/receipts",
    query: filters
  });
}

export function fetchReceipt(receiptId: string) {
  return httpClient<MaterialReceipt>({
    path: `/api/proxy/receipts/${receiptId}`
  });
}

export function createReceipt(payload: MaterialReceiptCreatePayload) {
  return httpClient<MaterialReceipt>({
    path: "/api/proxy/receipts",
    method: "POST",
    body: payload
  });
}
