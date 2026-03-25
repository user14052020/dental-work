import { useQuery } from "@tanstack/react-query";

import { fetchContractors } from "@/entities/contractors/api/contractors-api";
import { contractorsQueryKeys } from "@/entities/contractors/model/query-keys";
import { ContractorsFilters } from "@/entities/contractors/model/types";

export function useContractorsQuery(filters: ContractorsFilters) {
  return useQuery({
    queryKey: contractorsQueryKeys.list(filters),
    queryFn: () => fetchContractors(filters)
  });
}
