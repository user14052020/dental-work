import { useQuery } from "@tanstack/react-query";

import { fetchReports } from "@/entities/reports/api/reports-api";
import { reportsQueryKeys } from "@/entities/reports/model/query-keys";
import { ReportsFilters } from "@/entities/reports/model/types";

export function useReportsQuery(filters: ReportsFilters, options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: reportsQueryKeys.snapshot(filters),
    queryFn: () => fetchReports(filters),
    enabled: options?.enabled ?? true
  });
}
