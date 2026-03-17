"use client";

import { Button, Checkbox, Group, Modal, Stack, Textarea, TextInput } from "@mantine/core";
import { useForm } from "@mantine/form";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef } from "react";

import {
  createOperationCategory,
  updateOperationCategory
} from "@/entities/operations/api/operations-api";
import { operationsQueryKeys } from "@/entities/operations/model/query-keys";
import {
  ExecutorCategory,
  ExecutorCategoryCreatePayload,
  ExecutorCategoryUpdatePayload
} from "@/entities/operations/model/types";
import { showErrorNotification } from "@/shared/lib/notifications/show-error";
import { showSuccessNotification } from "@/shared/lib/notifications/show-success";

type ExecutorCategoryFormValues = {
  code: string;
  name: string;
  description: string;
  sort_order: string;
  is_active: boolean;
};

const emptyValues: ExecutorCategoryFormValues = {
  code: "",
  name: "",
  description: "",
  sort_order: "0",
  is_active: true
};

function buildCategoryPayload(values: ExecutorCategoryFormValues): ExecutorCategoryCreatePayload {
  return {
    code: values.code.trim(),
    name: values.name.trim(),
    sort_order: Number(values.sort_order || 0),
    is_active: values.is_active,
    ...(values.description.trim() ? { description: values.description.trim() } : {})
  };
}

function buildCategoryUpdatePayload(values: ExecutorCategoryFormValues): ExecutorCategoryUpdatePayload {
  return buildCategoryPayload(values);
}

type ExecutorCategoryFormModalProps = {
  opened: boolean;
  onClose: () => void;
  category?: ExecutorCategory | null;
};

export function ExecutorCategoryFormModal({
  opened,
  onClose,
  category
}: ExecutorCategoryFormModalProps) {
  const queryClient = useQueryClient();
  const syncedCategoryKeyRef = useRef<string | null>(null);
  const form = useForm<ExecutorCategoryFormValues>({
    initialValues: emptyValues,
    validate: {
      code: (value) => (value.trim().length >= 1 ? null : "Укажите код категории."),
      name: (value) => (value.trim().length >= 2 ? null : "Укажите название категории."),
      sort_order: (value) => (Number(value) >= 0 ? null : "Порядок сортировки должен быть неотрицательным.")
    }
  });

  useEffect(() => {
    if (!opened) {
      syncedCategoryKeyRef.current = null;
      return;
    }

    const nextSyncKey = category ? `${category.id}:${category.updated_at}` : "new";
    if (syncedCategoryKeyRef.current === nextSyncKey) {
      return;
    }

    syncedCategoryKeyRef.current = nextSyncKey;
    form.setValues(
      category
        ? {
            code: category.code,
            name: category.name,
            description: category.description ?? "",
            sort_order: String(category.sort_order),
            is_active: category.is_active
          }
        : emptyValues
    );
  }, [category, form, opened]);

  const mutation = useMutation({
    mutationFn: async (values: ExecutorCategoryFormValues) => {
      return category
        ? updateOperationCategory(category.id, buildCategoryUpdatePayload(values))
        : createOperationCategory(buildCategoryPayload(values));
    },
    onSuccess() {
      queryClient.invalidateQueries({ queryKey: operationsQueryKeys.root });
      showSuccessNotification(category ? "Категория оплаты обновлена." : "Категория оплаты добавлена.");
      onClose();
    },
    onError(error) {
      showErrorNotification(error, "Не удалось сохранить категорию оплаты.");
    }
  });

  return (
    <Modal
      opened={opened}
      onClose={onClose}
      size="lg"
      title={category ? "Редактирование категории оплаты" : "Новая категория оплаты"}
    >
      <form onSubmit={form.onSubmit((values) => mutation.mutate(values))}>
        <Stack gap="md">
          <Group grow>
            <TextInput label="Код" {...form.getInputProps("code")} />
            <TextInput label="Название" {...form.getInputProps("name")} />
          </Group>
          <Textarea
            label="Описание"
            minRows={3}
            placeholder="Например: техники с повышенным тарифом или отдельная производственная группа."
            {...form.getInputProps("description")}
          />
          <Group grow>
            <TextInput label="Порядок сортировки" type="number" {...form.getInputProps("sort_order")} />
            <Checkbox
              className="self-end pb-2"
              label="Категория активна"
              {...form.getInputProps("is_active", { type: "checkbox" })}
            />
          </Group>
          <Group justify="flex-end">
            <Button color="gray" type="button" variant="light" onClick={onClose}>
              Отмена
            </Button>
            <Button loading={mutation.isPending} type="submit">
              {category ? "Сохранить" : "Создать"}
            </Button>
          </Group>
        </Stack>
      </form>
    </Modal>
  );
}
