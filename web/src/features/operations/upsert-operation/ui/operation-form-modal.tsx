"use client";

import {
  ActionIcon,
  Button,
  Checkbox,
  Group,
  Modal,
  Select,
  Stack,
  Text,
  Textarea,
  TextInput
} from "@mantine/core";
import { useForm } from "@mantine/form";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { IconPlus, IconTrash } from "@tabler/icons-react";
import { useEffect, useRef } from "react";

import { createOperation, updateOperation } from "@/entities/operations/api/operations-api";
import { operationsQueryKeys } from "@/entities/operations/model/query-keys";
import {
  ExecutorCategory,
  OperationCatalog,
  OperationCatalogCreatePayload,
  OperationCatalogUpdatePayload
} from "@/entities/operations/model/types";
import { showErrorNotification } from "@/shared/lib/notifications/show-error";
import { showSuccessNotification } from "@/shared/lib/notifications/show-success";

type RateFormLine = {
  executor_category_id: string;
  labor_rate: string;
};

type OperationFormValues = {
  code: string;
  name: string;
  operation_group: string;
  description: string;
  default_quantity: string;
  default_duration_hours: string;
  sort_order: string;
  is_active: boolean;
  rates: RateFormLine[];
};

const emptyValues: OperationFormValues = {
  code: "",
  name: "",
  operation_group: "",
  description: "",
  default_quantity: "1",
  default_duration_hours: "0",
  sort_order: "0",
  is_active: true,
  rates: []
};

function buildRatesPayload(lines: RateFormLine[]) {
  const deduplicatedRates = new Map<string, string>();

  lines.forEach((line) => {
    if (!line.executor_category_id || line.labor_rate === "") {
      return;
    }

    deduplicatedRates.set(line.executor_category_id, line.labor_rate);
  });

  return Array.from(deduplicatedRates.entries()).map(([executor_category_id, labor_rate]) => ({
    executor_category_id,
    labor_rate
  }));
}

function buildOperationPayload(values: OperationFormValues): OperationCatalogCreatePayload {
  return {
    code: values.code.trim(),
    name: values.name.trim(),
    default_quantity: values.default_quantity || "1",
    default_duration_hours: values.default_duration_hours || "0",
    sort_order: Number(values.sort_order || 0),
    is_active: values.is_active,
    rates: buildRatesPayload(values.rates),
    ...(values.operation_group.trim() ? { operation_group: values.operation_group.trim() } : {}),
    ...(values.description.trim() ? { description: values.description.trim() } : {})
  };
}

function buildOperationUpdatePayload(values: OperationFormValues): OperationCatalogUpdatePayload {
  return buildOperationPayload(values);
}

type OperationFormModalProps = {
  opened: boolean;
  onClose: () => void;
  categories: ExecutorCategory[];
  operation?: OperationCatalog | null;
};

export function OperationFormModal({
  opened,
  onClose,
  categories,
  operation
}: OperationFormModalProps) {
  const queryClient = useQueryClient();
  const syncedOperationKeyRef = useRef<string | null>(null);
  const form = useForm<OperationFormValues>({
    initialValues: emptyValues,
    validate: {
      code: (value) => (value.trim().length >= 1 ? null : "Укажите код операции."),
      name: (value) => (value.trim().length >= 2 ? null : "Укажите название операции."),
      default_quantity: (value) => (Number(value) >= 0 ? null : "Количество должно быть неотрицательным."),
      default_duration_hours: (value) => (Number(value) >= 0 ? null : "Длительность должна быть неотрицательной."),
      sort_order: (value) => (Number(value) >= 0 ? null : "Порядок сортировки должен быть неотрицательным.")
    }
  });

  useEffect(() => {
    if (!opened) {
      syncedOperationKeyRef.current = null;
      return;
    }

    const nextSyncKey = operation ? `${operation.id}:${operation.updated_at}` : "new";
    if (syncedOperationKeyRef.current === nextSyncKey) {
      return;
    }

    syncedOperationKeyRef.current = nextSyncKey;
    form.setValues(
      operation
        ? {
            code: operation.code,
            name: operation.name,
            operation_group: operation.operation_group ?? "",
            description: operation.description ?? "",
            default_quantity: operation.default_quantity,
            default_duration_hours: operation.default_duration_hours,
            sort_order: String(operation.sort_order),
            is_active: operation.is_active,
            rates: operation.rates.map((rate) => ({
              executor_category_id: rate.executor_category_id,
              labor_rate: rate.labor_rate
            }))
          }
        : emptyValues
    );
  }, [form, opened, operation]);

  const mutation = useMutation({
    mutationFn: async (values: OperationFormValues) => {
      return operation
        ? updateOperation(operation.id, buildOperationUpdatePayload(values))
        : createOperation(buildOperationPayload(values));
    },
    onSuccess() {
      queryClient.invalidateQueries({ queryKey: operationsQueryKeys.root });
      showSuccessNotification(operation ? "Операция обновлена." : "Операция добавлена.");
      onClose();
    },
    onError(error) {
      showErrorNotification(error, "Не удалось сохранить операцию.");
    }
  });

  const categoryOptions = categories.map((category) => ({
    value: category.id,
    label: `${category.code} · ${category.name}`
  }));

  return (
    <Modal opened={opened} onClose={onClose} size="xl" title={operation ? "Редактирование операции" : "Новая операция"}>
      <form onSubmit={form.onSubmit((values) => mutation.mutate(values))}>
        <Stack gap="md">
          <div className="grid gap-3 md:grid-cols-2">
            <TextInput label="Код" {...form.getInputProps("code")} />
            <TextInput label="Название" {...form.getInputProps("name")} />
          </div>
          <div className="grid gap-3 md:grid-cols-3">
            <TextInput label="Группа" placeholder="Например, каркасы или керамика" {...form.getInputProps("operation_group")} />
            <TextInput label="Базовое количество" type="number" {...form.getInputProps("default_quantity")} />
            <TextInput label="Нормо-часы" type="number" {...form.getInputProps("default_duration_hours")} />
          </div>
          <Textarea label="Описание" minRows={3} {...form.getInputProps("description")} />
          <div className="grid gap-3 md:grid-cols-2">
            <TextInput label="Порядок сортировки" type="number" {...form.getInputProps("sort_order")} />
            <Checkbox
              className="self-end pb-2"
              label="Операция активна"
              {...form.getInputProps("is_active", { type: "checkbox" })}
            />
          </div>

          <div className="rounded-[24px] bg-slate-50/80 p-4">
            <Group justify="space-between" align="center">
              <div>
                <Text fw={700}>Тарифы по категориям оплаты</Text>
                <Text c="dimmed" size="sm">
                  Эти ставки используются при расчете оплаты технику в заказе.
                </Text>
              </div>
              <Button
                leftSection={<IconPlus size={16} />}
                type="button"
                variant="light"
                onClick={() =>
                  form.insertListItem("rates", {
                    executor_category_id: "",
                    labor_rate: "0"
                  })
                }
              >
                Добавить тариф
              </Button>
            </Group>

            <Stack gap="sm" mt="md">
              {form.values.rates.length ? (
                form.values.rates.map((rate, index) => (
                  <div key={`${rate.executor_category_id}-${index}`} className="rounded-[20px] bg-white p-4 shadow-sm">
                    <div className="grid gap-3 md:grid-cols-[1.5fr_1fr_auto] md:items-end">
                      <Select
                        data={categoryOptions}
                        label="Категория оплаты"
                        placeholder="Выберите категорию"
                        value={rate.executor_category_id || null}
                        onChange={(value) => form.setFieldValue(`rates.${index}.executor_category_id`, value ?? "")}
                      />
                      <TextInput
                        label="Ставка за операцию"
                        type="number"
                        value={rate.labor_rate}
                        onChange={(event) =>
                          form.setFieldValue(`rates.${index}.labor_rate`, event.currentTarget.value)
                        }
                      />
                      <ActionIcon
                        color="red"
                        mb={4}
                        mt="auto"
                        size="lg"
                        variant="light"
                        onClick={() => form.removeListItem("rates", index)}
                      >
                        <IconTrash size={16} />
                      </ActionIcon>
                    </div>
                  </div>
                ))
              ) : (
                <Text c="dimmed" size="sm">
                  Если тарифы не заполнены, операция останется доступной, но оплата технику по категориям не рассчитается автоматически.
                </Text>
              )}
            </Stack>
          </div>

          <Group justify="flex-end">
            <Button color="gray" type="button" variant="light" onClick={onClose}>
              Отмена
            </Button>
            <Button loading={mutation.isPending} type="submit">
              {operation ? "Сохранить" : "Создать"}
            </Button>
          </Group>
        </Stack>
      </form>
    </Modal>
  );
}
