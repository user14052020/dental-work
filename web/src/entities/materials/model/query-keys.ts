import { MaterialsFilters } from "@/entities/materials/model/types";

export const materialsQueryKeys = {
  root: ["materials"] as const,
  list: (filters: MaterialsFilters) => [...materialsQueryKeys.root, "list", filters] as const,
  detail: (materialId?: string) => [...materialsQueryKeys.root, "detail", materialId] as const
};
