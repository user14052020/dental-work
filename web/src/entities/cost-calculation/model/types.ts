export type CostMaterialLineInput = {
  material_id: string;
  quantity: string;
  unit_cost_override?: string;
};

export type CostCalculationPayload = {
  materials: CostMaterialLineInput[];
  labor_hours: string;
  hourly_rate_override?: string;
  executor_id?: string;
  additional_expenses: string;
  sale_price: string;
};

export type CostBreakdownLine = {
  name: string;
  quantity: string;
  unit_cost: string;
  total_cost: string;
};

export type CostCalculationResult = {
  materials_cost: string;
  labor_cost: string;
  additional_expenses: string;
  total_cost: string;
  sale_price: string;
  margin: string;
  profitability_percent: string;
  lines: CostBreakdownLine[];
};
