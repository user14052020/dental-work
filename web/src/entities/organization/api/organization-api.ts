import {
  OrganizationProfile,
  OrganizationProfilePayload
} from "@/entities/organization/model/types";
import { httpClient } from "@/shared/api/http-client";

export function fetchOrganizationProfile() {
  return httpClient<OrganizationProfile>({
    path: "/api/proxy/organization"
  });
}

export function updateOrganizationProfile(payload: OrganizationProfilePayload) {
  return httpClient<OrganizationProfile>({
    path: "/api/proxy/organization",
    method: "PUT",
    body: payload
  });
}
