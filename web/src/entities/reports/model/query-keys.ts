import { ReportsFilters } from "@/entities/reports/model/types";

export const reportsQueryKeys = {
  root: ["reports"] as const,
  snapshot: (filters: ReportsFilters) => [...reportsQueryKeys.root, "snapshot", filters] as const
};
