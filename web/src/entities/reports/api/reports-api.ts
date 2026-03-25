import { ReportsFilters, ReportsSnapshot } from "@/entities/reports/model/types";
import { httpClient } from "@/shared/api/http-client";

export function fetchReports(filters: ReportsFilters) {
  return httpClient<ReportsSnapshot>({
    path: "/api/proxy/reports",
    query: filters
  });
}
