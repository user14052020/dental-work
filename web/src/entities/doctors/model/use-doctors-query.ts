import { useQuery } from "@tanstack/react-query";

import { fetchDoctors } from "@/entities/doctors/api/doctors-api";
import { doctorsQueryKeys } from "@/entities/doctors/model/query-keys";
import { DoctorsFilters } from "@/entities/doctors/model/types";

export function useDoctorsQuery(filters: DoctorsFilters) {
  return useQuery({
    queryKey: doctorsQueryKeys.list(filters),
    queryFn: () => fetchDoctors(filters)
  });
}
