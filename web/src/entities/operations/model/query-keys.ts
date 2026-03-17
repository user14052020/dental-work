import {
  ExecutorCategoriesFilters,
  OperationsFilters
} from "@/entities/operations/model/types";

export const operationsQueryKeys = {
  root: ["operations"] as const,
  categories: (filters: ExecutorCategoriesFilters) =>
    [...operationsQueryKeys.root, "categories", filters] as const,
  list: (filters: OperationsFilters) => [...operationsQueryKeys.root, "list", filters] as const
};
