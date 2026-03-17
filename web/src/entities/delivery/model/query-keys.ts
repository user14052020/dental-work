import { DeliveryFilters } from "@/entities/delivery/model/types";

export const deliveryQueryKeys = {
  root: ["delivery"] as const,
  list: (filters: DeliveryFilters) => [...deliveryQueryKeys.root, "list", filters] as const
};
