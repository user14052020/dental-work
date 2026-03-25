import { useQuery } from "@tanstack/react-query";

import {
  fetchInventoryAdjustment,
  fetchInventoryAdjustments
} from "@/entities/inventory-adjustments/api/inventory-adjustments-api";
import { inventoryAdjustmentsQueryKeys } from "@/entities/inventory-adjustments/model/query-keys";
import { InventoryAdjustmentFilters } from "@/entities/inventory-adjustments/model/types";

export function useInventoryAdjustmentsQuery(filters: InventoryAdjustmentFilters) {
  return useQuery({
    queryKey: inventoryAdjustmentsQueryKeys.list(filters),
    queryFn: () => fetchInventoryAdjustments(filters)
  });
}

export function useInventoryAdjustmentDetailQuery(adjustmentId?: string) {
  return useQuery({
    queryKey: inventoryAdjustmentsQueryKeys.detail(adjustmentId),
    queryFn: () => fetchInventoryAdjustment(adjustmentId as string),
    enabled: Boolean(adjustmentId)
  });
}
