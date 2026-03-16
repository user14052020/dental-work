export const dashboardQueryKeys = {
  root: ["dashboard"] as const,
  detail: () => [...dashboardQueryKeys.root, "detail"] as const
};
