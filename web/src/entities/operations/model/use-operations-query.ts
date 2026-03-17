import { useQuery } from "@tanstack/react-query";

import {
  fetchOperationCategories,
  fetchOperations
} from "@/entities/operations/api/operations-api";
import { operationsQueryKeys } from "@/entities/operations/model/query-keys";
import {
  ExecutorCategoriesFilters,
  OperationsFilters
} from "@/entities/operations/model/types";

export function useOperationCategoriesQuery(filters: ExecutorCategoriesFilters) {
  return useQuery({
    queryKey: operationsQueryKeys.categories(filters),
    queryFn: () => fetchOperationCategories(filters)
  });
}

export function useOperationsQuery(filters: OperationsFilters) {
  return useQuery({
    queryKey: operationsQueryKeys.list(filters),
    queryFn: () => fetchOperations(filters)
  });
}
