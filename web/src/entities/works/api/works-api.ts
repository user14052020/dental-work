import {
  WorkAttachment,
  Work,
  WorkClosePayload,
  WorkCreatePayload,
  WorkReopenPayload,
  WorksFilters,
  WorksResponse,
  WorkUpdateStatusPayload
} from "@/entities/works/model/types";
import { WorkOperationStatusUpdatePayload } from "@/entities/operations/model/types";
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

export function closeWork(workId: string, payload: WorkClosePayload) {
  return httpClient<Work>({
    path: `/api/proxy/works/${workId}/close`,
    method: "POST",
    body: payload
  });
}

export function reopenWork(workId: string, payload: WorkReopenPayload) {
  return httpClient<Work>({
    path: `/api/proxy/works/${workId}/reopen`,
    method: "POST",
    body: payload
  });
}

export function updateWorkOperationStatus(
  workId: string,
  workOperationId: string,
  payload: WorkOperationStatusUpdatePayload
) {
  return httpClient<Work>({
    path: `/api/proxy/works/${workId}/operations/${workOperationId}/status`,
    method: "PATCH",
    body: payload
  });
}

export function uploadWorkAttachment(workId: string, file: File) {
  const formData = new FormData();
  formData.append("file", file);

  return httpClient<WorkAttachment>({
    path: `/api/proxy/works/${workId}/attachments`,
    method: "POST",
    body: formData
  });
}

export function deleteWorkAttachment(workId: string, attachmentId: string) {
  return httpClient<void>({
    path: `/api/proxy/works/${workId}/attachments/${attachmentId}`,
    method: "DELETE"
  });
}
