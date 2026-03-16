import {
  Executor,
  ExecutorCreatePayload,
  ExecutorsFilters,
  ExecutorsResponse,
  ExecutorUpdatePayload
} from "@/entities/executors/model/types";
import { httpClient } from "@/shared/api/http-client";

export function fetchExecutors(filters: ExecutorsFilters) {
  return httpClient<ExecutorsResponse>({
    path: "/api/proxy/executors",
    query: filters
  });
}

export function fetchExecutor(executorId: string) {
  return httpClient<Executor>({
    path: `/api/proxy/executors/${executorId}`
  });
}

export function createExecutor(payload: ExecutorCreatePayload) {
  return httpClient<Executor>({
    path: "/api/proxy/executors",
    method: "POST",
    body: payload
  });
}

export function updateExecutor(executorId: string, payload: ExecutorUpdatePayload) {
  return httpClient<Executor>({
    path: `/api/proxy/executors/${executorId}`,
    method: "PATCH",
    body: payload
  });
}

export function archiveExecutor(executorId: string) {
  return httpClient<Executor>({
    path: `/api/proxy/executors/${executorId}/archive`,
    method: "POST"
  });
}
