"use client";

import { Button, Checkbox, Group, Modal, Stack, Textarea, TextInput } from "@mantine/core";
import { useForm } from "@mantine/form";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef } from "react";

import { createExecutor, updateExecutor } from "@/entities/executors/api/executors-api";
import { executorsQueryKeys } from "@/entities/executors/model/query-keys";
import {
  Executor,
  ExecutorCreatePayload,
  ExecutorUpdatePayload
} from "@/entities/executors/model/types";
import { showErrorNotification } from "@/shared/lib/notifications/show-error";
import { showSuccessNotification } from "@/shared/lib/notifications/show-success";

type ExecutorFormValues = {
  full_name: string;
  phone: string;
  email: string;
  specialization: string;
  hourly_rate: string;
  comment: string;
  is_active: boolean;
};

const emptyValues: ExecutorFormValues = {
  full_name: "",
  phone: "",
  email: "",
  specialization: "",
  hourly_rate: "0",
  comment: "",
  is_active: true
};

function buildExecutorPayload(values: ExecutorFormValues): ExecutorCreatePayload {
  return {
    full_name: values.full_name.trim(),
    hourly_rate: values.hourly_rate,
    is_active: values.is_active,
    ...(values.phone.trim() ? { phone: values.phone.trim() } : {}),
    ...(values.email.trim() ? { email: values.email.trim() } : {}),
    ...(values.specialization.trim() ? { specialization: values.specialization.trim() } : {}),
    ...(values.comment.trim() ? { comment: values.comment.trim() } : {})
  };
}

function buildExecutorUpdatePayload(values: ExecutorFormValues): ExecutorUpdatePayload {
  return buildExecutorPayload(values);
}

type ExecutorFormModalProps = {
  opened: boolean;
  onClose: () => void;
  executor?: Executor | null;
};

export function ExecutorFormModal({ opened, onClose, executor }: ExecutorFormModalProps) {
  const queryClient = useQueryClient();
  const syncedExecutorKeyRef = useRef<string | null>(null);
  const form = useForm<ExecutorFormValues>({
    initialValues: emptyValues,
    validate: {
      full_name: (value) => (value.trim().length >= 3 ? null : "Введите ФИО исполнителя."),
      hourly_rate: (value) => (Number(value) >= 0 ? null : "Ставка должна быть неотрицательной.")
    }
  });

  useEffect(() => {
    if (!opened) {
      syncedExecutorKeyRef.current = null;
      return;
    }

    const nextSyncKey = executor ? `${executor.id}:${executor.updated_at}` : "new";

    if (syncedExecutorKeyRef.current === nextSyncKey) {
      return;
    }

    syncedExecutorKeyRef.current = nextSyncKey;
    form.setValues(
      executor
        ? {
            full_name: executor.full_name,
            phone: executor.phone ?? "",
            email: executor.email ?? "",
            specialization: executor.specialization ?? "",
            hourly_rate: executor.hourly_rate,
            comment: executor.comment ?? "",
            is_active: executor.is_active
          }
        : emptyValues
    );
  }, [executor, form, opened]);

  const mutation = useMutation({
    mutationFn: async (values: ExecutorFormValues) => {
      return executor
        ? updateExecutor(executor.id, buildExecutorUpdatePayload(values))
        : createExecutor(buildExecutorPayload(values));
    },
    onSuccess() {
      queryClient.invalidateQueries({ queryKey: executorsQueryKeys.root });
      showSuccessNotification(executor ? "Карточка исполнителя обновлена." : "Исполнитель добавлен.");
      onClose();
    },
    onError(error) {
      showErrorNotification(error, "Не удалось сохранить исполнителя.");
    }
  });

  return (
    <Modal opened={opened} onClose={onClose} size="lg" title={executor ? "Редактирование исполнителя" : "Новый исполнитель"}>
      <form onSubmit={form.onSubmit((values) => mutation.mutate(values))}>
        <Stack gap="md">
          <TextInput label="ФИО" {...form.getInputProps("full_name")} />
          <Group grow>
            <TextInput label="Телефон" {...form.getInputProps("phone")} />
            <TextInput label="Эл. почта" {...form.getInputProps("email")} />
          </Group>
          <Group grow>
            <TextInput label="Специализация" {...form.getInputProps("specialization")} />
            <TextInput label="Ставка / час" type="number" {...form.getInputProps("hourly_rate")} />
          </Group>
          <Textarea label="Комментарий" minRows={3} {...form.getInputProps("comment")} />
          <Checkbox label="Активный исполнитель" {...form.getInputProps("is_active", { type: "checkbox" })} />
          <Group justify="flex-end">
            <Button color="gray" type="button" variant="light" onClick={onClose}>
              Отмена
            </Button>
            <Button loading={mutation.isPending} type="submit">
              {executor ? "Сохранить" : "Создать"}
            </Button>
          </Group>
        </Stack>
      </form>
    </Modal>
  );
}
