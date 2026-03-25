import {
  ClientDocumentEmailPayload,
  DocumentEmailResult,
  NaradDocumentEmailPayload
} from "@/entities/documents/model/types";
import { httpClient } from "@/shared/api/http-client";

export function sendNaradDocumentEmail(naradId: string, payload: NaradDocumentEmailPayload) {
  return httpClient<DocumentEmailResult>({
    path: `/api/proxy/documents/narads/${naradId}/email`,
    method: "POST",
    body: payload
  });
}

export function sendClientDocumentEmail(clientId: string, payload: ClientDocumentEmailPayload) {
  return httpClient<DocumentEmailResult>({
    path: `/api/proxy/documents/clients/${clientId}/email`,
    method: "POST",
    body: payload
  });
}
