import { useQuery } from "@tanstack/react-query";

import { fetchWorkCatalogItems } from "@/entities/work-catalog/api/work-catalog-api";
import { workCatalogQueryKeys } from "@/entities/work-catalog/model/query-keys";
import { WorkCatalogFilters } from "@/entities/work-catalog/model/types";

export function useWorkCatalogQuery(filters: WorkCatalogFilters) {
  return useQuery({
    queryKey: workCatalogQueryKeys.list(filters),
    queryFn: () => fetchWorkCatalogItems(filters)
  });
}
