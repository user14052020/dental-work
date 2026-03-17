"use client";

import { ActionIcon, Button, Checkbox, Modal, Select, Stack, Text, TextInput, Textarea } from "@mantine/core";
import { useForm } from "@mantine/form";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { IconPlus, IconTrash } from "@tabler/icons-react";
import { useEffect, useRef } from "react";

import { useOperationsQuery } from "@/entities/operations/model/use-operations-query";
import { createWorkCatalogItem, updateWorkCatalogItem } from "@/entities/work-catalog/api/work-catalog-api";
import { workCatalogQueryKeys } from "@/entities/work-catalog/model/query-keys";
import {
  WorkCatalogItem,
  WorkCatalogItemCreatePayload,
  WorkCatalogItemUpdatePayload
} from "@/entities/work-catalog/model/types";
import { showErrorNotification } from "@/shared/lib/notifications/show-error";
import { showSuccessNotification } from "@/shared/lib/notifications/show-success";

type WorkCatalogTemplateLine = {
  operation_id: string;
  quantity: string;
  note: string;
  sort_order: string;
};

type WorkCatalogFormValues = {
  code: string;
  name: string;
  category: string;
  description: string;
  base_price: string;
  default_duration_hours: string;
  sort_order: string;
  is_active: boolean;
  default_operations: WorkCatalogTemplateLine[];
};

const emptyValues: WorkCatalogFormValues = {
  code: "",
  name: "",
  category: "",
  description: "",
  base_price: "0",
  default_duration_hours: "0",
  sort_order: "0",
  is_active: true,
  default_operations: []
};

function buildWorkCatalogPayload(values: WorkCatalogFormValues): WorkCatalogItemCreatePayload {
  return {
    code: values.code.trim(),
    name: values.name.trim(),
    base_price: values.base_price || "0",
    default_duration_hours: values.default_duration_hours || "0",
    sort_order: Number(values.sort_order || 0),
    is_active: values.is_active,
    default_operations: values.default_operations
      .filter((line) => line.operation_id)
      .map((line, index) => ({
        operation_id: line.operation_id,
        quantity: line.quantity || "1",
        sort_order: Number(line.sort_order || index),
        ...(line.note.trim() ? { note: line.note.trim() } : {})
      })),
    ...(values.category.trim() ? { category: values.category.trim() } : {}),
    ...(values.description.trim() ? { description: values.description.trim() } : {})
  };
}

function buildWorkCatalogUpdatePayload(values: WorkCatalogFormValues): WorkCatalogItemUpdatePayload {
  return buildWorkCatalogPayload(values);
}

type WorkCatalogItemFormModalProps = {
  item?: WorkCatalogItem | null;
  opened: boolean;
  onClose: () => void;
};

export function WorkCatalogItemFormModal({
  item,
  opened,
  onClose
}: WorkCatalogItemFormModalProps) {
  const queryClient = useQueryClient();
  const operationsQuery = useOperationsQuery({ page: 1, page_size: 100, active_only: true });
  const syncedItemKeyRef = useRef<string | null>(null);
  const form = useForm<WorkCatalogFormValues>({
    initialValues: emptyValues,
    validate: {
      code: (value) => (value.trim().length >= 1 ? null : "Укажите код."),
      name: (value) => (value.trim().length >= 2 ? null : "Укажите название.")
    }
  });

  useEffect(() => {
    if (!opened) {
      syncedItemKeyRef.current = null;
      return;
    }

    const nextSyncKey = item ? `${item.id}:${item.updated_at}` : "new";
    if (syncedItemKeyRef.current === nextSyncKey) {
      return;
    }

    syncedItemKeyRef.current = nextSyncKey;
    form.setValues(
      item
        ? {
            code: item.code,
            name: item.name,
            category: item.category ?? "",
            description: item.description ?? "",
            base_price: item.base_price,
            default_duration_hours: item.default_duration_hours,
            sort_order: String(item.sort_order),
            is_active: item.is_active,
            default_operations: item.default_operations.map((operation) => ({
              operation_id: operation.operation_id,
              quantity: operation.quantity,
              note: operation.note ?? "",
              sort_order: String(operation.sort_order)
            }))
          }
        : emptyValues
    );
  }, [form, item, opened]);

  const mutation = useMutation({
    mutationFn: async (values: WorkCatalogFormValues) =>
      item
        ? updateWorkCatalogItem(item.id, buildWorkCatalogUpdatePayload(values))
        : createWorkCatalogItem(buildWorkCatalogPayload(values)),
    onSuccess() {
      queryClient.invalidateQueries({ queryKey: workCatalogQueryKeys.root });
      showSuccessNotification(item ? "Позиция каталога обновлена." : "Позиция каталога добавлена.");
      onClose();
    },
    onError(error) {
      showErrorNotification(error, "Не удалось сохранить позицию каталога.");
    }
  });

  const operationOptions =
    operationsQuery.data?.items.map((operation) => ({
      value: operation.id,
      label: `${operation.code} · ${operation.name}`
    })) ?? [];

  return (
    <Modal
      opened={opened}
      onClose={onClose}
      size="xl"
      title={item ? "Редактирование позиции каталога" : "Новая позиция каталога"}
    >
      <form onSubmit={form.onSubmit((values) => mutation.mutate(values))}>
        <Stack gap="md">
          <div className="grid gap-3 md:grid-cols-2">
            <TextInput label="Код" {...form.getInputProps("code")} />
            <TextInput label="Название" {...form.getInputProps("name")} />
          </div>
          <div className="grid gap-3 md:grid-cols-3">
            <TextInput label="Категория" {...form.getInputProps("category")} />
            <TextInput label="Базовая цена" type="number" {...form.getInputProps("base_price")} />
            <TextInput
              label="Нормо-часы"
              type="number"
              {...form.getInputProps("default_duration_hours")}
            />
          </div>
          <Textarea label="Описание" minRows={3} {...form.getInputProps("description")} />
          <div className="grid gap-3 md:grid-cols-2">
            <TextInput label="Порядок сортировки" type="number" {...form.getInputProps("sort_order")} />
            <Checkbox
              className="self-end pb-2"
              label="Позиция активна"
              {...form.getInputProps("is_active", { type: "checkbox" })}
            />
          </div>

          <div className="rounded-[24px] bg-slate-50/80 p-4">
            <Button
              leftSection={<IconPlus size={16} />}
              type="button"
              variant="light"
              onClick={() =>
                form.insertListItem("default_operations", {
                  operation_id: "",
                  quantity: "1",
                  note: "",
                  sort_order: String(form.values.default_operations.length)
                })
              }
            >
              Добавить шаблон операции
            </Button>

            <Stack gap="sm" mt="md">
              {form.values.default_operations.length ? (
                form.values.default_operations.map((line, index) => (
                  <div key={`${line.operation_id}-${index}`} className="rounded-[20px] bg-white p-4 shadow-sm">
                    <div className="grid gap-3 md:grid-cols-[1.6fr_100px_140px_auto] md:items-end">
                      <Select
                        data={operationOptions}
                        label="Операция"
                        placeholder="Выберите операцию"
                        value={line.operation_id || null}
                        onChange={(value) =>
                          form.setFieldValue(`default_operations.${index}.operation_id`, value ?? "")
                        }
                      />
                      <TextInput
                        label="Кол-во"
                        type="number"
                        value={line.quantity}
                        onChange={(event) =>
                          form.setFieldValue(`default_operations.${index}.quantity`, event.currentTarget.value)
                        }
                      />
                      <TextInput
                        label="Сортировка"
                        type="number"
                        value={line.sort_order}
                        onChange={(event) =>
                          form.setFieldValue(`default_operations.${index}.sort_order`, event.currentTarget.value)
                        }
                      />
                      <ActionIcon
                        color="red"
                        mb={4}
                        mt="auto"
                        size="lg"
                        variant="light"
                        onClick={() => form.removeListItem("default_operations", index)}
                      >
                        <IconTrash size={16} />
                      </ActionIcon>
                    </div>
                    <TextInput
                      label="Примечание"
                      mt="sm"
                      value={line.note}
                      onChange={(event) =>
                        form.setFieldValue(`default_operations.${index}.note`, event.currentTarget.value)
                      }
                    />
                  </div>
                ))
              ) : (
                <Text c="dimmed" size="sm">
                  Шаблон операций пока не задан. При выборе позиции каталога в новой работе операции не подставятся автоматически.
                </Text>
              )}
            </Stack>
          </div>

          <Button loading={mutation.isPending} type="submit">
            {item ? "Сохранить" : "Создать"}
          </Button>
        </Stack>
      </form>
    </Modal>
  );
}
