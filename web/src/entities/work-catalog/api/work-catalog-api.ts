import {
  WorkCatalogFilters,
  WorkCatalogItem,
  WorkCatalogItemCreatePayload,
  WorkCatalogItemUpdatePayload,
  WorkCatalogResponse
} from "@/entities/work-catalog/model/types";
import { httpClient } from "@/shared/api/http-client";

export function fetchWorkCatalogItems(filters: WorkCatalogFilters) {
  return httpClient<WorkCatalogResponse>({
    path: "/api/proxy/work-catalog",
    query: filters
  });
}

export function createWorkCatalogItem(payload: WorkCatalogItemCreatePayload) {
  return httpClient<WorkCatalogItem>({
    path: "/api/proxy/work-catalog",
    method: "POST",
    body: payload
  });
}

export function updateWorkCatalogItem(itemId: string, payload: WorkCatalogItemUpdatePayload) {
  return httpClient<WorkCatalogItem>({
    path: `/api/proxy/work-catalog/${itemId}`,
    method: "PATCH",
    body: payload
  });
}
