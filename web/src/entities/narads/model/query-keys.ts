import { NaradsFilters, OutsideWorksFilters } from "@/entities/narads/model/types";

export const naradsQueryKeys = {
  root: ["narads"] as const,
  list: (filters: NaradsFilters) => [...naradsQueryKeys.root, "list", filters] as const,
  detail: (naradId?: string) => [...naradsQueryKeys.root, "detail", naradId] as const,
  outsideWorks: (filters: OutsideWorksFilters) => [...naradsQueryKeys.root, "outside-works", filters] as const
};
