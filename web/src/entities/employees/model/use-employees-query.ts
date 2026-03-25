import { useQuery } from "@tanstack/react-query";

import { fetchEmployees } from "@/entities/employees/api/employees-api";
import { employeesQueryKeys } from "@/entities/employees/model/query-keys";
import { EmployeesFilters } from "@/entities/employees/model/types";

export function useEmployeesQuery(filters: EmployeesFilters) {
  return useQuery({
    queryKey: employeesQueryKeys.list(filters),
    queryFn: () => fetchEmployees(filters)
  });
}
