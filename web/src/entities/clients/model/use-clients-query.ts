import { useQuery } from "@tanstack/react-query";

import { fetchClient, fetchClients } from "@/entities/clients/api/clients-api";
import { clientsQueryKeys } from "@/entities/clients/model/query-keys";
import { ClientsFilters } from "@/entities/clients/model/types";

export function useClientsQuery(filters: ClientsFilters) {
  return useQuery({
    queryKey: clientsQueryKeys.list(filters),
    queryFn: () => fetchClients(filters)
  });
}

export function useClientDetailQuery(clientId?: string) {
  return useQuery({
    queryKey: clientsQueryKeys.detail(clientId),
    queryFn: () => fetchClient(clientId as string),
    enabled: Boolean(clientId)
  });
}
