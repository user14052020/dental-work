import {
  DeliveryFilters,
  DeliveryMarkSentPayload,
  DeliveryMarkSentResponse,
  DeliveryResponse
} from "@/entities/delivery/model/types";
import { httpClient } from "@/shared/api/http-client";

export function fetchDeliveryItems(filters: DeliveryFilters) {
  return httpClient<DeliveryResponse>({
    path: "/api/proxy/delivery",
    query: filters
  });
}

export function markDeliverySent(payload: DeliveryMarkSentPayload) {
  return httpClient<DeliveryMarkSentResponse>({
    path: "/api/proxy/delivery/mark-sent",
    method: "POST",
    body: payload
  });
}

export function buildDeliveryManifestUrl(workIds: string[]) {
  const params = new URLSearchParams();
  workIds.forEach((workId) => {
    params.append("work_ids", workId);
  });
  return `/api/proxy/delivery/manifest?${params.toString()}`;
}
