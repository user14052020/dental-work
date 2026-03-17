import { useQuery } from "@tanstack/react-query";

import { fetchOrganizationProfile } from "@/entities/organization/api/organization-api";
import { organizationQueryKeys } from "@/entities/organization/model/query-keys";

export function useOrganizationProfileQuery() {
  return useQuery({
    queryKey: organizationQueryKeys.detail(),
    queryFn: fetchOrganizationProfile
  });
}
