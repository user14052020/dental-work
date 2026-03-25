"use client";

import { Button, Checkbox, Modal, Stack, TextInput, Textarea } from "@mantine/core";
import { useForm } from "@mantine/form";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef } from "react";

import { createContractor, updateContractor } from "@/entities/contractors/api/contractors-api";
import { contractorsQueryKeys } from "@/entities/contractors/model/query-keys";
import {
  Contractor,
  ContractorCreatePayload,
  ContractorUpdatePayload
} from "@/entities/contractors/model/types";
import { showErrorNotification } from "@/shared/lib/notifications/show-error";
import { showSuccessNotification } from "@/shared/lib/notifications/show-success";

type ContractorFormValues = {
  name: string;
  contact_person: string;
  phone: string;
  email: string;
  address: string;
  comment: string;
  is_active: boolean;
};

const emptyValues: ContractorFormValues = {
  name: "",
  contact_person: "",
  phone: "",
  email: "",
  address: "",
  comment: "",
  is_active: true
};

function buildPayload(values: ContractorFormValues): ContractorCreatePayload {
  return {
    name: values.name.trim(),
    is_active: values.is_active,
    ...(values.contact_person.trim() ? { contact_person: values.contact_person.trim() } : {}),
    ...(values.phone.trim() ? { phone: values.phone.trim() } : {}),
    ...(values.email.trim() ? { email: values.email.trim() } : {}),
    ...(values.address.trim() ? { address: values.address.trim() } : {}),
    ...(values.comment.trim() ? { comment: values.comment.trim() } : {})
  };
}

function buildUpdatePayload(values: ContractorFormValues): ContractorUpdatePayload {
  return buildPayload(values);
}

type ContractorFormModalProps = {
  contractor?: Contractor | null;
  opened: boolean;
  onClose: () => void;
};

export function ContractorFormModal({ contractor, opened, onClose }: ContractorFormModalProps) {
  const queryClient = useQueryClient();
  const syncedKeyRef = useRef<string | null>(null);
  const form = useForm<ContractorFormValues>({
    initialValues: emptyValues,
    validate: {
      name: (value) => (value.trim().length >= 2 ? null : "Укажите название подрядчика.")
    }
  });

  useEffect(() => {
    if (!opened) {
      syncedKeyRef.current = null;
      return;
    }

    const nextKey = contractor ? `${contractor.id}:${contractor.updated_at}` : "new";
    if (syncedKeyRef.current === nextKey) {
      return;
    }

    syncedKeyRef.current = nextKey;
    const nextValues = contractor
      ? {
          name: contractor.name,
          contact_person: contractor.contact_person ?? "",
          phone: contractor.phone ?? "",
          email: contractor.email ?? "",
          address: contractor.address ?? "",
          comment: contractor.comment ?? "",
          is_active: contractor.is_active
        }
      : emptyValues;
    form.setValues(nextValues);
    form.resetDirty(nextValues);
  }, [contractor, form, opened]);

  const mutation = useMutation({
    mutationFn: async (values: ContractorFormValues) =>
      contractor ? updateContractor(contractor.id, buildUpdatePayload(values)) : createContractor(buildPayload(values)),
    onSuccess() {
      queryClient.invalidateQueries({ queryKey: contractorsQueryKeys.root });
      showSuccessNotification(contractor ? "Карточка подрядчика обновлена." : "Подрядчик добавлен.");
      onClose();
    },
    onError(error) {
      showErrorNotification(error, "Не удалось сохранить подрядчика.");
    }
  });

  return (
    <Modal opened={opened} onClose={onClose} size="lg" title={contractor ? "Редактирование подрядчика" : "Новый подрядчик"}>
      <form onSubmit={form.onSubmit((values) => mutation.mutate(values))}>
        <Stack gap="md">
          <TextInput label="Название" {...form.getInputProps("name")} />
          <div className="grid gap-3 md:grid-cols-2">
            <TextInput label="Контактное лицо" {...form.getInputProps("contact_person")} />
            <TextInput label="Телефон" {...form.getInputProps("phone")} />
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            <TextInput label="Email" {...form.getInputProps("email")} />
            <TextInput label="Адрес" {...form.getInputProps("address")} />
          </div>
          <Textarea label="Комментарий" minRows={3} {...form.getInputProps("comment")} />
          <Checkbox label="Подрядчик активен" {...form.getInputProps("is_active", { type: "checkbox" })} />
          <Button loading={mutation.isPending} type="submit">
            {contractor ? "Сохранить" : "Создать"}
          </Button>
        </Stack>
      </form>
    </Modal>
  );
}
