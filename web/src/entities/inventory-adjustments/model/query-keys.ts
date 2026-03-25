import { InventoryAdjustmentFilters } from "@/entities/inventory-adjustments/model/types";

export const inventoryAdjustmentsQueryKeys = {
  root: ["inventory-adjustments"] as const,
  list: (filters: InventoryAdjustmentFilters) => [...inventoryAdjustmentsQueryKeys.root, "list", filters] as const,
  detail: (adjustmentId?: string) => [...inventoryAdjustmentsQueryKeys.root, "detail", adjustmentId] as const
};
