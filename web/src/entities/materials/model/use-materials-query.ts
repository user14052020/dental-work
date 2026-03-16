import { useQuery } from "@tanstack/react-query";

import { fetchMaterial, fetchMaterials } from "@/entities/materials/api/materials-api";
import { materialsQueryKeys } from "@/entities/materials/model/query-keys";
import { MaterialsFilters } from "@/entities/materials/model/types";

export function useMaterialsQuery(filters: MaterialsFilters) {
  return useQuery({
    queryKey: materialsQueryKeys.list(filters),
    queryFn: () => fetchMaterials(filters)
  });
}

export function useMaterialDetailQuery(materialId?: string) {
  return useQuery({
    queryKey: materialsQueryKeys.detail(materialId),
    queryFn: () => fetchMaterial(materialId as string),
    enabled: Boolean(materialId)
  });
}
