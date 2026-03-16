export type DashboardTopItem = {
  id: string;
  name?: string | null;
  full_name?: string | null;
  work_count: number;
  amount: string;
};

export type DashboardSnapshot = {
  active_works: number;
  overdue_works: number;
  revenue: string;
  profit: string;
  material_expenses: string;
  top_clients: DashboardTopItem[];
  top_executors: DashboardTopItem[];
  generated_at: string;
};
