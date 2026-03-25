import { ContractorsFilters } from "@/entities/contractors/model/types";

export const contractorsQueryKeys = {
  root: ["contractors"] as const,
  list: (filters: ContractorsFilters) => [...contractorsQueryKeys.root, "list", filters] as const
};
