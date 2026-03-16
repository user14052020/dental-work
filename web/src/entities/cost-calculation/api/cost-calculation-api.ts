import {
  CostCalculationPayload,
  CostCalculationResult
} from "@/entities/cost-calculation/model/types";
import { httpClient } from "@/shared/api/http-client";

export function calculateCost(payload: CostCalculationPayload) {
  return httpClient<CostCalculationResult>({
    path: "/api/proxy/cost-calculation/estimate",
    method: "POST",
    body: payload
  });
}
