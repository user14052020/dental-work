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

export function buildDeliveryManifestUrl(naradIds: string[]) {
  const params = new URLSearchParams();
  naradIds.forEach((naradId) => {
    params.append("narad_ids", naradId);
  });
  return `/api/proxy/delivery/manifest?${params.toString()}`;
}
