import {
  Work,
  WorkCreatePayload,
  WorksFilters,
  WorksResponse,
  WorkUpdateStatusPayload
} from "@/entities/works/model/types";
import { httpClient } from "@/shared/api/http-client";

export function fetchWorks(filters: WorksFilters) {
  return httpClient<WorksResponse>({
    path: "/api/proxy/works",
    query: filters
  });
}

export function fetchWork(workId: string) {
  return httpClient<Work>({
    path: `/api/proxy/works/${workId}`
  });
}

export function createWork(payload: WorkCreatePayload) {
  return httpClient<Work>({
    path: "/api/proxy/works",
    method: "POST",
    body: payload
  });
}

export function updateWorkStatus(workId: string, payload: WorkUpdateStatusPayload) {
  return httpClient<Work>({
    path: `/api/proxy/works/${workId}/status`,
    method: "PATCH",
    body: payload
  });
}
