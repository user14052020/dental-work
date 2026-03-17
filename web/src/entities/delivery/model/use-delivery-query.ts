import { useQuery } from "@tanstack/react-query";

import { fetchDeliveryItems } from "@/entities/delivery/api/delivery-api";
import { deliveryQueryKeys } from "@/entities/delivery/model/query-keys";
import { DeliveryFilters } from "@/entities/delivery/model/types";

export function useDeliveryQuery(filters: DeliveryFilters) {
  return useQuery({
    queryKey: deliveryQueryKeys.list(filters),
    queryFn: () => fetchDeliveryItems(filters)
  });
}
