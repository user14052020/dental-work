import {
  Contractor,
  ContractorCreatePayload,
  ContractorsFilters,
  ContractorsResponse,
  ContractorUpdatePayload
} from "@/entities/contractors/model/types";
import { httpClient } from "@/shared/api/http-client";

export function fetchContractors(filters: ContractorsFilters) {
  return httpClient<ContractorsResponse>({
    path: "/api/proxy/contractors",
    query: filters
  });
}

export function createContractor(payload: ContractorCreatePayload) {
  return httpClient<Contractor>({
    path: "/api/proxy/contractors",
    method: "POST",
    body: payload
  });
}

export function updateContractor(contractorId: string, payload: ContractorUpdatePayload) {
  return httpClient<Contractor>({
    path: `/api/proxy/contractors/${contractorId}`,
    method: "PATCH",
    body: payload
  });
}
