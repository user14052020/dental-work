import {
  Material,
  MaterialConsumePayload,
  MaterialCreatePayload,
  MaterialsFilters,
  MaterialsResponse,
  MaterialUpdatePayload
} from "@/entities/materials/model/types";
import { httpClient } from "@/shared/api/http-client";

export function fetchMaterials(filters: MaterialsFilters) {
  return httpClient<MaterialsResponse>({
    path: "/api/proxy/materials",
    query: filters
  });
}

export function fetchMaterial(materialId: string) {
  return httpClient<Material>({
    path: `/api/proxy/materials/${materialId}`
  });
}

export function createMaterial(payload: MaterialCreatePayload) {
  return httpClient<Material>({
    path: "/api/proxy/materials",
    method: "POST",
    body: payload
  });
}

export function updateMaterial(materialId: string, payload: MaterialUpdatePayload) {
  return httpClient<Material>({
    path: `/api/proxy/materials/${materialId}`,
    method: "PATCH",
    body: payload
  });
}

export function consumeMaterial(materialId: string, payload: MaterialConsumePayload) {
  return httpClient<Material>({
    path: `/api/proxy/materials/${materialId}/consume`,
    method: "POST",
    body: payload
  });
}
