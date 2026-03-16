import { useQuery } from "@tanstack/react-query";

import { fetchExecutor, fetchExecutors } from "@/entities/executors/api/executors-api";
import { executorsQueryKeys } from "@/entities/executors/model/query-keys";
import { ExecutorsFilters } from "@/entities/executors/model/types";

export function useExecutorsQuery(filters: ExecutorsFilters) {
  return useQuery({
    queryKey: executorsQueryKeys.list(filters),
    queryFn: () => fetchExecutors(filters)
  });
}

export function useExecutorDetailQuery(executorId?: string) {
  return useQuery({
    queryKey: executorsQueryKeys.detail(executorId),
    queryFn: () => fetchExecutor(executorId as string),
    enabled: Boolean(executorId)
  });
}
