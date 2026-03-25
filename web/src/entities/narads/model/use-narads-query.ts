import { useQuery } from "@tanstack/react-query";

import { fetchNarad, fetchNarads, fetchOutsideWorks } from "@/entities/narads/api/narads-api";
import { naradsQueryKeys } from "@/entities/narads/model/query-keys";
import { NaradsFilters, OutsideWorksFilters } from "@/entities/narads/model/types";

export function useNaradsQuery(filters: NaradsFilters) {
  return useQuery({
    queryKey: naradsQueryKeys.list(filters),
    queryFn: () => fetchNarads(filters)
  });
}

export function useNaradDetailQuery(naradId?: string) {
  return useQuery({
    queryKey: naradsQueryKeys.detail(naradId),
    queryFn: () => fetchNarad(naradId as string),
    enabled: Boolean(naradId)
  });
}

export function useOutsideWorksQuery(filters: OutsideWorksFilters) {
  return useQuery({
    queryKey: naradsQueryKeys.outsideWorks(filters),
    queryFn: () => fetchOutsideWorks(filters)
  });
}
