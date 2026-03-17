import {
  ExecutorCategoriesFilters,
  ExecutorCategoriesResponse,
  ExecutorCategory,
  ExecutorCategoryCreatePayload,
  ExecutorCategoryUpdatePayload,
  OperationCatalog,
  OperationCatalogCreatePayload,
  OperationsFilters,
  OperationsResponse,
  OperationCatalogUpdatePayload
} from "@/entities/operations/model/types";
import { httpClient } from "@/shared/api/http-client";

export function fetchOperationCategories(filters: ExecutorCategoriesFilters) {
  return httpClient<ExecutorCategoriesResponse>({
    path: "/api/proxy/operations/categories",
    query: filters
  });
}

export function createOperationCategory(payload: ExecutorCategoryCreatePayload) {
  return httpClient<ExecutorCategory>({
    path: "/api/proxy/operations/categories",
    method: "POST",
    body: payload
  });
}

export function updateOperationCategory(categoryId: string, payload: ExecutorCategoryUpdatePayload) {
  return httpClient<ExecutorCategory>({
    path: `/api/proxy/operations/categories/${categoryId}`,
    method: "PATCH",
    body: payload
  });
}

export function fetchOperations(filters: OperationsFilters) {
  return httpClient<OperationsResponse>({
    path: "/api/proxy/operations",
    query: filters
  });
}

export function createOperation(payload: OperationCatalogCreatePayload) {
  return httpClient<OperationCatalog>({
    path: "/api/proxy/operations",
    method: "POST",
    body: payload
  });
}

export function updateOperation(operationId: string, payload: OperationCatalogUpdatePayload) {
  return httpClient<OperationCatalog>({
    path: `/api/proxy/operations/${operationId}`,
    method: "PATCH",
    body: payload
  });
}
