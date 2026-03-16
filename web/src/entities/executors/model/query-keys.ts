import { ExecutorsFilters } from "@/entities/executors/model/types";

export const executorsQueryKeys = {
  root: ["executors"] as const,
  list: (filters: ExecutorsFilters) => [...executorsQueryKeys.root, "list", filters] as const,
  detail: (executorId?: string) => [...executorsQueryKeys.root, "detail", executorId] as const
};
