import { DashboardSnapshot } from "@/entities/dashboard/model/types";
import { httpClient } from "@/shared/api/http-client";

export function fetchDashboard() {
  return httpClient<DashboardSnapshot>({
    path: "/api/proxy/dashboard"
  });
}
