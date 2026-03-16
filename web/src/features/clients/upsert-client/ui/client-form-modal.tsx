"use client";

import { Button, Group, Modal, Stack, Textarea, TextInput } from "@mantine/core";
import { useForm } from "@mantine/form";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef } from "react";

import { createClient, updateClient } from "@/entities/clients/api/clients-api";
import { clientsQueryKeys } from "@/entities/clients/model/query-keys";
import { Client, ClientCreatePayload, ClientUpdatePayload } from "@/entities/clients/model/types";
import { showErrorNotification } from "@/shared/lib/notifications/show-error";
import { showSuccessNotification } from "@/shared/lib/notifications/show-success";

type ClientFormValues = {
  name: string;
  contact_person: string;
  phone: string;
  email: string;
  address: string;
  comment: string;
};

type ClientFormModalProps = {
  opened: boolean;
  onClose: () => void;
  client?: Client | null;
};

const emptyValues: ClientFormValues = {
  name: "",
  contact_person: "",
  phone: "",
  email: "",
  address: "",
  comment: ""
};

function buildClientPayload(values: ClientFormValues): ClientCreatePayload {
  return {
    name: values.name.trim(),
    ...(values.contact_person.trim() ? { contact_person: values.contact_person.trim() } : {}),
    ...(values.phone.trim() ? { phone: values.phone.trim() } : {}),
    ...(values.email.trim() ? { email: values.email.trim() } : {}),
    ...(values.address.trim() ? { address: values.address.trim() } : {}),
    ...(values.comment.trim() ? { comment: values.comment.trim() } : {})
  };
}

function buildClientUpdatePayload(values: ClientFormValues): ClientUpdatePayload {
  return buildClientPayload(values);
}

export function ClientFormModal({ opened, onClose, client }: ClientFormModalProps) {
  const queryClient = useQueryClient();
  const syncedClientKeyRef = useRef<string | null>(null);
  const form = useForm<ClientFormValues>({
    initialValues: emptyValues,
    validate: {
      name: (value) => (value.trim().length >= 2 ? null : "Название должно быть не короче 2 символов.")
    }
  });

  useEffect(() => {
    if (!opened) {
      syncedClientKeyRef.current = null;
      return;
    }

    const nextSyncKey = client ? `${client.id}:${client.updated_at}` : "new";

    if (syncedClientKeyRef.current === nextSyncKey) {
      return;
    }

    syncedClientKeyRef.current = nextSyncKey;
    form.setValues(
      client
        ? {
            name: client.name,
            contact_person: client.contact_person ?? "",
            phone: client.phone ?? "",
            email: client.email ?? "",
            address: client.address ?? "",
            comment: client.comment ?? ""
          }
        : emptyValues
    );
  }, [client, form, opened]);

  const mutation = useMutation({
    mutationFn: async (values: ClientFormValues) => {
      return client
        ? updateClient(client.id, buildClientUpdatePayload(values))
        : createClient(buildClientPayload(values));
    },
    onSuccess() {
      queryClient.invalidateQueries({ queryKey: clientsQueryKeys.root });
      showSuccessNotification(client ? "Карточка клиента обновлена." : "Клиент добавлен.");
      onClose();
      form.reset();
    },
    onError(error) {
      showErrorNotification(error, "Не удалось сохранить клиента.");
    }
  });

  return (
    <Modal
      opened={opened}
      onClose={onClose}
      title={client ? "Редактирование клиента" : "Новый клиент"}
      size="lg"
    >
      <form onSubmit={form.onSubmit((values) => mutation.mutate(values))}>
        <Stack gap="md">
          <TextInput label="Название клиники / клиента" {...form.getInputProps("name")} />
          <TextInput label="Контактное лицо" {...form.getInputProps("contact_person")} />
          <Group grow>
            <TextInput label="Телефон" {...form.getInputProps("phone")} />
            <TextInput label="Эл. почта" {...form.getInputProps("email")} />
          </Group>
          <TextInput label="Адрес" {...form.getInputProps("address")} />
          <Textarea label="Комментарий" minRows={3} {...form.getInputProps("comment")} />
          <Group justify="flex-end">
            <Button color="gray" type="button" variant="light" onClick={onClose}>
              Отмена
            </Button>
            <Button loading={mutation.isPending} type="submit">
              {client ? "Сохранить изменения" : "Создать клиента"}
            </Button>
          </Group>
        </Stack>
      </form>
    </Modal>
  );
}
