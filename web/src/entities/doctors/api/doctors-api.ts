import {
  Doctor,
  DoctorCreatePayload,
  DoctorsFilters,
  DoctorsResponse,
  DoctorUpdatePayload
} from "@/entities/doctors/model/types";
import { httpClient } from "@/shared/api/http-client";

export function fetchDoctors(filters: DoctorsFilters) {
  return httpClient<DoctorsResponse>({
    path: "/api/proxy/doctors",
    query: filters
  });
}

export function createDoctor(payload: DoctorCreatePayload) {
  return httpClient<Doctor>({
    path: "/api/proxy/doctors",
    method: "POST",
    body: payload
  });
}

export function updateDoctor(doctorId: string, payload: DoctorUpdatePayload) {
  return httpClient<Doctor>({
    path: `/api/proxy/doctors/${doctorId}`,
    method: "PATCH",
    body: payload
  });
}
