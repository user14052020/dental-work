"use client";

import { Button, Group, Modal, Select, Stack, Text, TextInput } from "@mantine/core";
import { useForm } from "@mantine/form";
import { useMutation } from "@tanstack/react-query";
import { useEffect, useRef } from "react";

import { showErrorNotification } from "@/shared/lib/notifications/show-error";
import { showSuccessNotification } from "@/shared/lib/notifications/show-success";

type DocumentEmailModalValues = {
  kind: string;
  recipient_email: string;
  subject: string;
  date_from: string;
  date_to: string;
};

type DocumentEmailModalProps = {
  opened: boolean;
  onClose: () => void;
  title: string;
  description: string;
  defaultKind: string;
  defaultRecipientEmail?: string | null;
  kindOptions: Array<{ value: string; label: string }>;
  includeDateRange?: boolean;
  initialDateFrom?: string;
  initialDateTo?: string;
  sendEmail: (payload: {
    kind: string;
    recipient_email?: string;
    subject?: string;
    date_from?: string;
    date_to?: string;
  }) => Promise<{ recipient_email: string; subject: string }>;
};

export function DocumentEmailModal({
  opened,
  onClose,
  title,
  description,
  defaultKind,
  defaultRecipientEmail,
  kindOptions,
  includeDateRange = false,
  initialDateFrom = "",
  initialDateTo = "",
  sendEmail
}: DocumentEmailModalProps) {
  const syncedStateKeyRef = useRef<string | null>(null);
  const form = useForm<DocumentEmailModalValues>({
    initialValues: {
      kind: defaultKind,
      recipient_email: defaultRecipientEmail ?? "",
      subject: "",
      date_from: initialDateFrom,
      date_to: initialDateTo
    },
    validate: {
      recipient_email: (value) => (/^\S+@\S+$/.test(value) ? null : "Укажи корректный e-mail.")
    }
  });

  useEffect(() => {
    if (!opened) {
      syncedStateKeyRef.current = null;
      return;
    }

    const nextStateKey = JSON.stringify({
      defaultKind,
      defaultRecipientEmail: defaultRecipientEmail ?? "",
      initialDateFrom,
      initialDateTo,
      includeDateRange
    });

    if (syncedStateKeyRef.current === nextStateKey) {
      return;
    }

    syncedStateKeyRef.current = nextStateKey;
    const nextValues = {
      kind: defaultKind,
      recipient_email: defaultRecipientEmail ?? "",
      subject: "",
      date_from: initialDateFrom,
      date_to: initialDateTo
    };
    form.setValues(nextValues);
    form.resetDirty(nextValues);
  }, [defaultKind, defaultRecipientEmail, form, includeDateRange, initialDateFrom, initialDateTo, opened]);

  const mutation = useMutation({
    mutationFn: sendEmail,
    onSuccess(result) {
      showSuccessNotification(`Документ отправлен на ${result.recipient_email}.`);
      onClose();
    },
    onError(error) {
      showErrorNotification(error, "Не удалось отправить документ по почте.");
    }
  });

  return (
    <Modal opened={opened} onClose={onClose} centered title={title}>
      <form
        onSubmit={form.onSubmit((values) =>
          mutation.mutate({
            kind: values.kind,
            recipient_email: values.recipient_email.trim(),
            ...(values.subject.trim() ? { subject: values.subject.trim() } : {}),
            ...(includeDateRange && values.date_from ? { date_from: new Date(`${values.date_from}T00:00:00`).toISOString() } : {}),
            ...(includeDateRange && values.date_to ? { date_to: new Date(`${values.date_to}T23:59:59`).toISOString() } : {})
          })
        )}
      >
        <Stack gap="md">
          <Text c="dimmed" size="sm">
            {description}
          </Text>
          <Select label="Документ" data={kindOptions} {...form.getInputProps("kind")} />
          <TextInput label="E-mail получателя" {...form.getInputProps("recipient_email")} />
          <TextInput
            label="Тема письма"
            placeholder="Если пусто, тема будет сформирована автоматически"
            {...form.getInputProps("subject")}
          />
          {includeDateRange ? (
            <Group grow>
              <TextInput label="Период от" type="date" {...form.getInputProps("date_from")} />
              <TextInput label="Период до" type="date" {...form.getInputProps("date_to")} />
            </Group>
          ) : null}
          <Group justify="flex-end">
            <Button color="gray" variant="light" type="button" onClick={onClose}>
              Отмена
            </Button>
            <Button loading={mutation.isPending} type="submit">
              Отправить
            </Button>
          </Group>
        </Stack>
      </form>
    </Modal>
  );
}
