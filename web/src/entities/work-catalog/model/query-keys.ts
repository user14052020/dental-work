import { WorkCatalogFilters } from "@/entities/work-catalog/model/types";

export const workCatalogQueryKeys = {
  root: ["work-catalog"] as const,
  list: (filters: WorkCatalogFilters) => [...workCatalogQueryKeys.root, "list", filters] as const
};
