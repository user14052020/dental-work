import {
  Client,
  ClientCreatePayload,
  ClientDetail,
  ClientsFilters,
  ClientsResponse,
  ClientUpdatePayload
} from "@/entities/clients/model/types";
import { httpClient } from "@/shared/api/http-client";

export function fetchClients(filters: ClientsFilters) {
  return httpClient<ClientsResponse>({
    path: "/api/proxy/clients",
    query: filters
  });
}

export function fetchClient(clientId: string) {
  return httpClient<ClientDetail>({
    path: `/api/proxy/clients/${clientId}`
  });
}

export function createClient(payload: ClientCreatePayload) {
  return httpClient<Client>({
    path: "/api/proxy/clients",
    method: "POST",
    body: payload
  });
}

export function updateClient(clientId: string, payload: ClientUpdatePayload) {
  return httpClient<Client>({
    path: `/api/proxy/clients/${clientId}`,
    method: "PATCH",
    body: payload
  });
}

export function deleteClient(clientId: string) {
  return httpClient<void>({
    path: `/api/proxy/clients/${clientId}`,
    method: "DELETE"
  });
}
