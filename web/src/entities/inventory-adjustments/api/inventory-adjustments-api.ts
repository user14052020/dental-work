import {
  InventoryAdjustment,
  InventoryAdjustmentCreatePayload,
  InventoryAdjustmentFilters,
  InventoryAdjustmentsResponse
} from "@/entities/inventory-adjustments/model/types";
import { httpClient } from "@/shared/api/http-client";

export function fetchInventoryAdjustments(filters: InventoryAdjustmentFilters) {
  return httpClient<InventoryAdjustmentsResponse>({
    path: "/api/proxy/inventory-adjustments",
    query: filters
  });
}

export function fetchInventoryAdjustment(adjustmentId: string) {
  return httpClient<InventoryAdjustment>({
    path: `/api/proxy/inventory-adjustments/${adjustmentId}`
  });
}

export function createInventoryAdjustment(payload: InventoryAdjustmentCreatePayload) {
  return httpClient<InventoryAdjustment>({
    path: "/api/proxy/inventory-adjustments",
    method: "POST",
    body: payload
  });
}
