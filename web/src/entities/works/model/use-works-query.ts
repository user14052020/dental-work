import { useQuery } from "@tanstack/react-query";

import { fetchWork, fetchWorks } from "@/entities/works/api/works-api";
import { worksQueryKeys } from "@/entities/works/model/query-keys";
import { WorksFilters } from "@/entities/works/model/types";

export function useWorksQuery(filters: WorksFilters) {
  return useQuery({
    queryKey: worksQueryKeys.list(filters),
    queryFn: () => fetchWorks(filters)
  });
}

export function useWorkDetailQuery(workId?: string) {
  return useQuery({
    queryKey: worksQueryKeys.detail(workId),
    queryFn: () => fetchWork(workId as string),
    enabled: Boolean(workId)
  });
}
