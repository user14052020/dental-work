import { ClientsFilters } from "@/entities/clients/model/types";

export const clientsQueryKeys = {
  root: ["clients"] as const,
  list: (filters: ClientsFilters) => [...clientsQueryKeys.root, "list", filters] as const,
  detail: (clientId?: string) => [...clientsQueryKeys.root, "detail", clientId] as const
};
