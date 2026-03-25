export type ReportsSummary = {
  total_narads: number;
  open_narads: number;
  overdue_narads: number;
  total_revenue: string;
  total_paid: string;
  total_balance_due: string;
  low_stock_materials: number;
  payroll_total: string;
  actual_material_consumption_total: string;
};

export type ClientBalanceReportItem = {
  client_id: string;
  client_name: string;
  narads_count: number;
  works_count: number;
  total_price: string;
  amount_paid: string;
  balance_due: string;
  last_received_at?: string | null;
};

export type NaradReportItem = {
  narad_id: string;
  narad_number: string;
  title: string;
  client_name: string;
  doctor_name?: string | null;
  patient_name?: string | null;
  status: string;
  works_count: number;
  total_price: string;
  total_cost: string;
  total_margin: string;
  amount_paid: string;
  balance_due: string;
  received_at: string;
  deadline_at?: string | null;
  completed_at?: string | null;
  closed_at?: string | null;
  is_overdue: boolean;
};

export type ExecutorLoadReportItem = {
  executor_id: string;
  executor_name: string;
  active_works: number;
  closed_works: number;
  revenue_total: string;
  earnings_total: string;
  last_closed_at?: string | null;
};

export type MaterialStockReportItem = {
  material_id: string;
  name: string;
  category?: string | null;
  unit: string;
  stock: string;
  reserved_stock: string;
  available_stock: string;
  min_stock: string;
  stock_value: string;
  is_low_stock: boolean;
};

export type PayrollReportItem = {
  executor_id: string;
  executor_name: string;
  narads_count: number;
  operations_count: number;
  quantity_total: string;
  earnings_total: string;
  last_closed_at?: string | null;
};

export type PayrollOperationReportItem = {
  executor_id: string;
  executor_name: string;
  operation_code?: string | null;
  operation_name: string;
  narads_count: number;
  operations_count: number;
  quantity_total: string;
  earnings_total: string;
  last_closed_at?: string | null;
};

export type ActualMaterialConsumptionReportItem = {
  movement_id: string;
  movement_date: string;
  material_id: string;
  material_name: string;
  material_category?: string | null;
  unit: string;
  quantity: string;
  unit_cost: string;
  total_cost: string;
  balance_after: string;
  reason?: string | null;
};

export type NaradMaterialConsumptionReportItem = {
  movement_id: string;
  movement_date: string;
  narad_id: string;
  narad_number: string;
  narad_title: string;
  client_name: string;
  work_id: string;
  work_order_number: string;
  material_id: string;
  material_name: string;
  material_category?: string | null;
  unit: string;
  quantity: string;
  unit_cost: string;
  total_cost: string;
  balance_after: string;
  reason?: string | null;
};

export type ReportsSnapshot = {
  summary: ReportsSummary;
  client_balances: ClientBalanceReportItem[];
  narads: NaradReportItem[];
  executors: ExecutorLoadReportItem[];
  payroll: PayrollReportItem[];
  payroll_operations: PayrollOperationReportItem[];
  materials: MaterialStockReportItem[];
  actual_material_consumption: ActualMaterialConsumptionReportItem[];
  narad_material_consumption: NaradMaterialConsumptionReportItem[];
  generated_at: string;
};

export type ReportsFilters = {
  date_from?: string;
  date_to?: string;
};
