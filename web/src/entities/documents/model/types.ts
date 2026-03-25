export type NaradDocumentEmailKind = "invoice" | "act" | "job-order";
export type ClientDocumentEmailKind = "invoice" | "act";

export type DocumentEmailResult = {
  kind: string;
  recipient_email: string;
  subject: string;
};

export type NaradDocumentEmailPayload = {
  kind: NaradDocumentEmailKind;
  recipient_email?: string;
  subject?: string;
};

export type ClientDocumentEmailPayload = {
  kind: ClientDocumentEmailKind;
  recipient_email?: string;
  subject?: string;
  date_from?: string;
  date_to?: string;
};
