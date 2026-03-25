"use client";

import { Button, Group, Modal, Stack, Text, TextInput } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { useState } from "react";

import { sendClientDocumentEmail } from "@/entities/documents/api/documents-api";
import { ClientDocumentEmailPayload } from "@/entities/documents/model/types";
import { DocumentEmailModal } from "@/features/documents/send-document-email/ui/document-email-modal";

function toIsoStart(value: string) {
  return value ? new Date(`${value}T00:00:00`).toISOString() : "";
}

function toIsoEnd(value: string) {
  return value ? new Date(`${value}T23:59:59`).toISOString() : "";
}

function openPrintDocument(path: string) {
  if (typeof window === "undefined") {
    return;
  }
  window.open(path, "_blank", "noopener,noreferrer");
}

type ClientDocumentsModalProps = {
  clientId: string;
  clientName: string;
  clientEmail?: string | null;
  opened: boolean;
  onClose: () => void;
};

function buildDocumentUrl(clientId: string, kind: "invoice" | "act", dateFrom: string, dateTo: string) {
  const url = new URL(`/api/proxy/documents/clients/${clientId}/${kind}`, window.location.origin);
  const normalizedDateFrom = toIsoStart(dateFrom);
  const normalizedDateTo = toIsoEnd(dateTo);

  if (normalizedDateFrom) {
    url.searchParams.set("date_from", normalizedDateFrom);
  }
  if (normalizedDateTo) {
    url.searchParams.set("date_to", normalizedDateTo);
  }

  return url.toString();
}

export function ClientDocumentsModal({
  clientId,
  clientName,
  clientEmail,
  opened,
  onClose
}: ClientDocumentsModalProps) {
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [emailOpened, emailHandlers] = useDisclosure(false);

  return (
    <>
      <Modal opened={opened} onClose={onClose} title="Сгруппированные документы" centered>
        <Stack gap="md">
          <Text c="dimmed" size="sm">
            Печать общего счета или акта по закрытым нарядам клиента {clientName}. Период можно не задавать, тогда
            попадут все закрытые наряды клиента.
          </Text>
          <TextInput
            label="Дата закрытия от"
            type="date"
            value={dateFrom}
            onChange={(event) => setDateFrom(event.currentTarget.value)}
          />
          <TextInput
            label="Дата закрытия до"
            type="date"
            value={dateTo}
            onChange={(event) => setDateTo(event.currentTarget.value)}
          />
          <Group grow>
            <Button
              variant="light"
              onClick={() => openPrintDocument(buildDocumentUrl(clientId, "invoice", dateFrom, dateTo))}
            >
              Счет
            </Button>
            <Button variant="light" onClick={() => openPrintDocument(buildDocumentUrl(clientId, "act", dateFrom, dateTo))}>
              Акт
            </Button>
          </Group>
          <Button variant="default" onClick={emailHandlers.open}>
            Отправить по почте
          </Button>
        </Stack>
      </Modal>
      <DocumentEmailModal
        opened={emailOpened}
        onClose={emailHandlers.close}
        title="Отправка сгруппированного документа"
        description={`Отправка общего счета или акта по закрытым нарядам клиента ${clientName}.`}
        defaultKind="invoice"
        defaultRecipientEmail={clientEmail}
        includeDateRange
        initialDateFrom={dateFrom}
        initialDateTo={dateTo}
        kindOptions={[
          { value: "invoice", label: "Счет" },
          { value: "act", label: "Акт" }
        ]}
        sendEmail={(payload) => sendClientDocumentEmail(clientId, payload as ClientDocumentEmailPayload)}
      />
    </>
  );
}
