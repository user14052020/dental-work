import { DoctorsFilters } from "@/entities/doctors/model/types";

export const doctorsQueryKeys = {
  root: ["doctors"] as const,
  list: (filters: DoctorsFilters) => [...doctorsQueryKeys.root, "list", filters] as const
};
