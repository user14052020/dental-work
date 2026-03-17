export const organizationQueryKeys = {
  root: ["organization"] as const,
  detail: () => [...organizationQueryKeys.root, "detail"] as const
};
