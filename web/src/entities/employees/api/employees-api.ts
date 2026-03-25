import {
  Employee,
  EmployeeCreatePayload,
  EmployeesFilters,
  EmployeesResponse,
  EmployeeUpdatePayload
} from "@/entities/employees/model/types";
import { httpClient } from "@/shared/api/http-client";

export function fetchEmployees(filters: EmployeesFilters) {
  return httpClient<EmployeesResponse>({
    path: "/api/proxy/employees",
    query: filters
  });
}

export function createEmployee(payload: EmployeeCreatePayload) {
  return httpClient<Employee>({
    path: "/api/proxy/employees",
    method: "POST",
    body: payload
  });
}

export function updateEmployee(employeeId: string, payload: EmployeeUpdatePayload) {
  return httpClient<Employee>({
    path: `/api/proxy/employees/${employeeId}`,
    method: "PATCH",
    body: payload
  });
}
