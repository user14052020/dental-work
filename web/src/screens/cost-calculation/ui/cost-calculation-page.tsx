"use client";

import { useState } from "react";

import { CostCalculationResult } from "@/entities/cost-calculation/model/types";
import { CostCalculatorForm } from "@/features/cost-calculation/estimate-cost/ui/cost-calculator-form";
import { PageHeading } from "@/shared/ui/page-heading";

export function CostCalculationPage() {
  const [result, setResult] = useState<CostCalculationResult>();

  return (
    <PageHeading
      title="Расчет себестоимости"
      description="Калькулятор себестоимости в реальном времени: материалы, труд, дополнительные расходы, цена продажи и прибыль."
    >
      <CostCalculatorForm result={result} onResult={setResult} />
    </PageHeading>
  );
}
