import { EmployeesFilters } from "@/entities/employees/model/types";

export const employeesQueryKeys = {
  root: ["employees"] as const,
  list: (filters: EmployeesFilters) => [...employeesQueryKeys.root, "list", filters] as const
};
