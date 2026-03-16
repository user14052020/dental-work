import { WorksFilters } from "@/entities/works/model/types";

export const worksQueryKeys = {
  root: ["works"] as const,
  list: (filters: WorksFilters) => [...worksQueryKeys.root, "list", filters] as const,
  detail: (workId?: string) => [...worksQueryKeys.root, "detail", workId] as const
};
