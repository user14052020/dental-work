import { useQuery } from "@tanstack/react-query";

import { fetchDashboard } from "@/entities/dashboard/api/dashboard-api";
import { dashboardQueryKeys } from "@/entities/dashboard/model/query-keys";

export function useDashboardQuery() {
  return useQuery({
    queryKey: dashboardQueryKeys.detail(),
    queryFn: fetchDashboard
  });
}
