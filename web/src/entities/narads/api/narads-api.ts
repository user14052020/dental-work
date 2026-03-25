import {
  Narad,
  NaradClosePayload,
  NaradReopenPayload,
  OutsideWorkMarkReturnedPayload,
  OutsideWorkMarkSentPayload,
  OutsideWorksFilters,
  OutsideWorksResponse,
  NaradsFilters,
  NaradsResponse,
  NaradUpsertPayload
} from "@/entities/narads/model/types";
import { httpClient } from "@/shared/api/http-client";

export function fetchNarads(filters: NaradsFilters) {
  return httpClient<NaradsResponse>({
    path: "/api/proxy/narads",
    query: filters
  });
}

export function fetchOutsideWorks(filters: OutsideWorksFilters) {
  return httpClient<OutsideWorksResponse>({
    path: "/api/proxy/outside-works",
    query: filters
  });
}

export function fetchNarad(naradId: string) {
  return httpClient<Narad>({
    path: `/api/proxy/narads/${naradId}`
  });
}

export function createNarad(payload: NaradUpsertPayload) {
  return httpClient<Narad>({
    path: "/api/proxy/narads",
    method: "POST",
    body: payload
  });
}

export function updateNarad(naradId: string, payload: Partial<NaradUpsertPayload>) {
  return httpClient<Narad>({
    path: `/api/proxy/narads/${naradId}`,
    method: "PATCH",
    body: payload
  });
}

export function reserveNaradMaterials(naradId: string) {
  return httpClient<Narad>({
    path: `/api/proxy/narads/${naradId}/reserve-materials`,
    method: "POST"
  });
}

export function closeNarad(naradId: string, payload: NaradClosePayload) {
  return httpClient<Narad>({
    path: `/api/proxy/narads/${naradId}/close`,
    method: "POST",
    body: payload
  });
}

export function reopenNarad(naradId: string, payload: NaradReopenPayload) {
  return httpClient<Narad>({
    path: `/api/proxy/narads/${naradId}/reopen`,
    method: "POST",
    body: payload
  });
}

export function markOutsideWorkSent(naradId: string, payload: OutsideWorkMarkSentPayload) {
  return httpClient<Narad>({
    path: `/api/proxy/outside-works/${naradId}/mark-sent`,
    method: "POST",
    body: payload
  });
}

export function markOutsideWorkReturned(naradId: string, payload: OutsideWorkMarkReturnedPayload) {
  return httpClient<Narad>({
    path: `/api/proxy/outside-works/${naradId}/mark-returned`,
    method: "POST",
    body: payload
  });
}
