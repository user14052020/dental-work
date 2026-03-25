"use client";

import {
  ActionIcon,
  Button,
  Divider,
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

import { useClientDetailQuery } from "@/entities/clients/model/use-clients-query";
import { useExecutorsQuery } from "@/entities/executors/model/use-executors-query";
import {
  OperationCatalog,
  WorkOperationCreatePayload
} from "@/entities/operations/model/types";
import { useOperationsQuery } from "@/entities/operations/model/use-operations-query";
import { formatMaterialUnit } from "@/entities/materials/model/material-units";
import { useMaterialsQuery } from "@/entities/materials/model/use-materials-query";
import { naradsQueryKeys } from "@/entities/narads/model/query-keys";
import { useNaradDetailQuery, useNaradsQuery } from "@/entities/narads/model/use-narads-query";
import { Narad } from "@/entities/narads/model/types";
import { useWorkCatalogQuery } from "@/entities/work-catalog/model/use-work-catalog-query";
import { createWork } from "@/entities/works/api/works-api";
import { worksQueryKeys } from "@/entities/works/model/query-keys";
import {
  WorkItemInput,
  workStatusOptions
} from "@/entities/works/model/types";
import { formatCurrency } from "@/shared/lib/formatters/format-currency";
import { toDateTimeLocal, toIsoDateTime } from "@/shared/lib/formatters/format-date";
import { showErrorNotification } from "@/shared/lib/notifications/show-error";
import { showSuccessNotification } from "@/shared/lib/notifications/show-success";

const priceFieldStyles = {
  label: {
    display: "block",
    minHeight: "3.5rem"
  }
} as const;

type MaterialLine = {
  material_id: string;
  quantity: string;
};

type WorkOperationLine = {
  operation_id: string;
  executor_id: string;
  quantity: string;
  unit_labor_cost_override: string;
  note: string;
};

type WorkItemLine = {
  work_catalog_item_id: string;
  work_type: string;
  description: string;
  quantity: string;
  unit_price: string;
};

type WorkFormValues = {
  narad_id: string;
  executor_id: string;
  work_catalog_item_id: string;
  work_type: string;
  description: string;
  status: string;
  received_at: string;
  deadline_at: string;
  base_price_for_client: string;
  price_adjustment_percent: string;
  price_for_client: string;
  additional_expenses: string;
  labor_hours: string;
  work_items: WorkItemLine[];
  operations: WorkOperationLine[];
  materials: MaterialLine[];
};

function buildEmptyValues(initialNarad?: Narad | null): WorkFormValues {
  return {
    narad_id: initialNarad?.id ?? "",
    executor_id: "",
    work_catalog_item_id: "",
    work_type: "",
    description: "",
    status: "new",
    received_at: toDateTimeLocal(initialNarad?.received_at ?? new Date().toISOString()),
    deadline_at: toDateTimeLocal(initialNarad?.deadline_at),
    base_price_for_client: "0",
    price_adjustment_percent: "0",
    price_for_client: "0",
    additional_expenses: "0",
    labor_hours: "0",
    work_items: [],
    operations: [],
    materials: []
  };
}

type WorkFormModalProps = {
  opened: boolean;
  onClose: () => void;
  initialNarad?: Narad | null;
};

function calculateFinalPrice(basePrice: string, adjustmentPercent: string) {
  const base = Number(basePrice || 0);
  const adjustment = Number(adjustmentPercent || 0);
  const total = base * (1 + adjustment / 100);
  return Number.isFinite(total) ? total.toFixed(2) : "0.00";
}

function getResolvedOperationRate(
  operation: OperationCatalog | undefined,
  categoryId: string | undefined,
  override: string
) {
  if (override.trim() !== "") {
    return Number(override || 0);
  }

  if (!operation || !categoryId) {
    return 0;
  }

  const matchedRate = operation.rates.find((rate) => rate.executor_category_id === categoryId);
  return Number(matchedRate?.labor_rate ?? 0);
}

function buildOperationPayload(lines: WorkOperationLine[]): WorkOperationCreatePayload[] {
  return lines
    .filter((line) => line.operation_id && Number(line.quantity || 0) > 0)
    .map((line) => ({
      operation_id: line.operation_id,
      quantity: line.quantity || "1",
      ...(line.executor_id ? { executor_id: line.executor_id } : {}),
      ...(line.unit_labor_cost_override.trim()
        ? { unit_labor_cost_override: line.unit_labor_cost_override.trim() }
        : {}),
      ...(line.note.trim() ? { note: line.note.trim() } : {})
    }));
}

function resolveCatalogPrice(clientDetail: { work_catalog_prices: Array<{ work_catalog_item_id: string; price: string }> } | undefined, catalogItemId: string, fallbackPrice: string) {
  const matchedPrice = clientDetail?.work_catalog_prices.find((item) => item.work_catalog_item_id === catalogItemId);
  return {
    hasClientPrice: Boolean(matchedPrice),
    price: matchedPrice?.price ?? fallbackPrice
  };
}

function buildWorkItemsPayload(values: WorkFormValues): WorkItemInput[] | undefined {
  const extraItems = values.work_items
    .filter(
      (item) =>
        item.work_catalog_item_id ||
        item.description.trim() ||
        Number(item.quantity || 0) > 0 ||
        Number(item.unit_price || 0) > 0
    )
    .map((item) => ({
      ...(item.work_catalog_item_id ? { work_catalog_item_id: item.work_catalog_item_id } : {}),
      ...(item.description.trim() ? { description: item.description.trim() } : {}),
      quantity: item.quantity || "1",
      ...(item.unit_price.trim() ? { unit_price: item.unit_price.trim() } : {})
    }));

  if (!extraItems.length) {
    return undefined;
  }

  return [
    {
      ...(values.work_catalog_item_id ? { work_catalog_item_id: values.work_catalog_item_id } : {}),
      ...(values.description.trim() ? { description: values.description.trim() } : {}),
      quantity: "1",
      unit_price: calculateFinalPrice(values.base_price_for_client, values.price_adjustment_percent)
    },
    ...extraItems
  ];
}

export function WorkFormModal({ opened, onClose, initialNarad }: WorkFormModalProps) {
  const queryClient = useQueryClient();
  const syncedWorkKeyRef = useRef<string | null>(null);
  const syncedNaradContextKeyRef = useRef<string | null>(null);
  const naradsQuery = useNaradsQuery({ page: 1, page_size: 100 });
  const executorsQuery = useExecutorsQuery({ page: 1, page_size: 100 });
  const workCatalogQuery = useWorkCatalogQuery({ page: 1, page_size: 100, active_only: true });
  const operationsQuery = useOperationsQuery({ page: 1, page_size: 100, active_only: true });
  const materialsQuery = useMaterialsQuery({ page: 1, page_size: 100 });
  const form = useForm<WorkFormValues>({
    initialValues: buildEmptyValues(initialNarad),
    validate: {
      narad_id: (value) => (value ? null : "Выберите наряд."),
      executor_id: (value) => (value ? null : "Выберите исполнителя."),
      work_catalog_item_id: (value) => (value ? null : "Выберите позицию каталога."),
      work_items: (items) =>
        items.some(
          (item) =>
            (item.description.trim() || Number(item.quantity || 0) > 0 || Number(item.unit_price || 0) > 0) &&
            !item.work_catalog_item_id
        )
          ? "Для каждой дополнительной позиции выберите позицию каталога."
          : null
    }
  });
  const selectedNaradDetailQuery = useNaradDetailQuery(
    !initialNarad && form.values.narad_id ? form.values.narad_id : undefined
  );
  const selectedNaradContext = initialNarad ?? (form.values.narad_id ? selectedNaradDetailQuery.data : undefined);
  const selectedClientDetailQuery = useClientDetailQuery(selectedNaradContext?.client_id);

  const executors = executorsQuery.data?.items ?? [];
  const operations = operationsQuery.data?.items ?? [];
  const workCatalogItems = workCatalogQuery.data?.items;
  const openNarads = (naradsQuery.data?.items ?? []).filter((narad) => !narad.is_closed);
  const executorsById = new Map(executors.map((executor) => [executor.id, executor]));
  const operationsById = new Map(operations.map((operation) => [operation.id, operation]));
  const workCatalogById = new Map((workCatalogItems ?? []).map((item) => [item.id, item]));
  const naradContextLocked = Boolean(form.values.narad_id);

  useEffect(() => {
    if (!opened) {
      syncedWorkKeyRef.current = null;
      return;
    }

    const nextSyncKey = initialNarad ? `${initialNarad.id}:${initialNarad.updated_at}` : "new";
    if (syncedWorkKeyRef.current === nextSyncKey) {
      return;
    }

    syncedWorkKeyRef.current = nextSyncKey;
    syncedNaradContextKeyRef.current = null;
    const nextValues = buildEmptyValues(initialNarad);
    form.setValues(nextValues);
    form.resetDirty(nextValues);
  }, [form, initialNarad, opened]);

  useEffect(() => {
    if (!opened) {
      syncedNaradContextKeyRef.current = null;
      return;
    }

    if (!selectedNaradContext) {
      return;
    }

    const nextContextKey = `${selectedNaradContext.id}:${selectedNaradContext.updated_at}`;
    if (syncedNaradContextKeyRef.current === nextContextKey) {
      return;
    }

    syncedNaradContextKeyRef.current = nextContextKey;
    form.setFieldValue("narad_id", selectedNaradContext.id);
    form.setFieldValue("received_at", toDateTimeLocal(selectedNaradContext.received_at));
    form.setFieldValue("deadline_at", toDateTimeLocal(selectedNaradContext.deadline_at));
  }, [form, opened, selectedNaradContext]);

  const mutation = useMutation({
    mutationFn: () => {
      const workItemsPayload = buildWorkItemsPayload(form.values);

      return createWork({
        narad_id: form.values.narad_id,
        executor_id: form.values.executor_id,
        work_catalog_item_id: form.values.work_catalog_item_id,
        description: form.values.description || undefined,
        status: form.values.status as never,
        received_at: toIsoDateTime(form.values.received_at) as string,
        deadline_at: toIsoDateTime(form.values.deadline_at),
        base_price_for_client: form.values.base_price_for_client,
        price_adjustment_percent: form.values.price_adjustment_percent,
        price_for_client: calculateFinalPrice(form.values.base_price_for_client, form.values.price_adjustment_percent),
        additional_expenses: form.values.additional_expenses,
        labor_hours: form.values.labor_hours,
        ...(workItemsPayload ? { work_items: workItemsPayload } : {}),
        operations: buildOperationPayload(form.values.operations),
        materials: form.values.materials.filter((item) => item.material_id && Number(item.quantity) > 0)
      });
    },
    onSuccess() {
      queryClient.invalidateQueries({ queryKey: worksQueryKeys.root });
      queryClient.invalidateQueries({ queryKey: naradsQueryKeys.root });
      showSuccessNotification("Работа создана.");
      form.setValues(buildEmptyValues(initialNarad));
      onClose();
    },
    onError(error) {
      showErrorNotification(error, "Не удалось создать работу.");
    }
  });

  const materialOptions =
    materialsQuery.data?.items.map((material) => ({
      value: material.id,
      label: `${material.name} · ${formatMaterialUnit(material.unit)}`
    })) ?? [];
  const executorOptions = executors.map((executor) => ({
    value: executor.id,
    label: executor.payment_category_name
      ? `${executor.full_name} · ${executor.payment_category_name}`
      : executor.full_name
  }));
  const operationOptions = operations.map((operation) => ({
    value: operation.id,
    label: `${operation.code} · ${operation.name}`
  }));
  const workCatalogOptions = (workCatalogItems ?? []).map((item) => ({
    value: item.id,
    label: `${item.code} · ${item.name}`
  }));
  const naradOptions = [
    ...(initialNarad && !openNarads.some((narad) => narad.id === initialNarad.id)
      ? [
          {
            value: initialNarad.id,
            label: `${initialNarad.narad_number} · ${initialNarad.client_name} · ${initialNarad.title}`
          }
        ]
      : []),
    ...openNarads.map((narad) => ({
      value: narad.id,
      label: `${narad.narad_number} · ${narad.client_name} · ${narad.title}`
    }))
  ];
  const finalPrice = calculateFinalPrice(form.values.base_price_for_client, form.values.price_adjustment_percent);
  const selectedCatalogLocked = Boolean(form.values.work_catalog_item_id);

  const operationLinesPreview = form.values.operations.map((line) => {
    const operation = operationsById.get(line.operation_id);
    const resolvedExecutor = executorsById.get(line.executor_id || form.values.executor_id);
    const resolvedRate = getResolvedOperationRate(
      operation,
      resolvedExecutor?.payment_category_id ?? undefined,
      line.unit_labor_cost_override
    );
    const quantity = Number(line.quantity || operation?.default_quantity || 0);
    return {
      operation,
      resolvedExecutor,
      resolvedRate,
      total: resolvedRate * quantity
    };
  });

  const calculatedOperationsLabor = operationLinesPreview.reduce((sum, line) => sum + line.total, 0);

  useEffect(() => {
    const catalogItemId = form.values.work_catalog_item_id;
    if (!catalogItemId) {
      return;
    }

    const catalogItem = workCatalogItems?.find((item) => item.id === catalogItemId);
    if (!catalogItem) {
      return;
    }

    const resolvedPrice = resolveCatalogPrice(
      selectedClientDetailQuery.data,
      catalogItem.id,
      catalogItem.base_price
    );
    const nextAdjustment = resolvedPrice.hasClientPrice
      ? "0"
      : (selectedClientDetailQuery.data?.default_price_adjustment_percent ?? "0");

    if (form.values.base_price_for_client !== resolvedPrice.price) {
      form.setFieldValue("base_price_for_client", resolvedPrice.price);
    }
    if (form.values.price_adjustment_percent !== nextAdjustment) {
      form.setFieldValue("price_adjustment_percent", nextAdjustment);
    }
  }, [
    form,
    form.values.base_price_for_client,
    form.values.price_adjustment_percent,
    form.values.work_catalog_item_id,
    selectedClientDetailQuery.data,
    workCatalogItems
  ]);

  return (
    <Modal opened={opened} onClose={onClose} size="xl" title="Новая работа">
      <form onSubmit={form.onSubmit(() => mutation.mutate())}>
        <Stack gap="md">
          {initialNarad ? (
            <Text c="dimmed" size="sm">
              Работа будет добавлена в наряд {initialNarad.narad_number} · {initialNarad.title}
            </Text>
          ) : null}
          {selectedNaradContext ? (
            <Text c="dimmed" size="sm">
              Заказчик: {selectedNaradContext.client_name} · Пациент: {selectedNaradContext.patient_name ?? "—"} · Врач:{" "}
              {selectedNaradContext.doctor_name ?? "—"}
            </Text>
          ) : null}
          <div className="grid gap-3 md:grid-cols-3">
            <Select
              data={naradOptions}
              disabled={Boolean(initialNarad)}
              error={form.errors.narad_id}
              label="Наряд"
              placeholder="Выберите открытый наряд"
              searchable
              value={form.values.narad_id || null}
              onChange={(value) => {
                form.setFieldValue("narad_id", value ?? "");
                syncedNaradContextKeyRef.current = null;
              }}
            />
            <Select
              data={workCatalogOptions}
              error={form.errors.work_catalog_item_id}
              label="Позиция каталога"
              placeholder="Выберите работу из каталога"
              searchable
              value={form.values.work_catalog_item_id || null}
              onChange={(value) => {
                const nextItem = workCatalogById.get(value ?? "");
                form.setFieldValue("work_catalog_item_id", value ?? "");
                if (!nextItem) {
                  form.setFieldValue("work_type", "");
                  return;
                }

                form.setFieldValue("work_type", nextItem.name);
                form.setFieldValue("description", nextItem.description ?? "");
                form.setFieldValue("labor_hours", nextItem.default_duration_hours);
                form.setFieldValue(
                  "operations",
                  nextItem.default_operations.map((operation) => ({
                    operation_id: operation.operation_id,
                    executor_id: "",
                    quantity: operation.quantity,
                    unit_labor_cost_override: "",
                    note: operation.note ?? ""
                  }))
                );
              }}
            />
            <TextInput
              label="Тип работы"
              placeholder="Подставляется из позиции каталога"
              readOnly
              {...form.getInputProps("work_type")}
            />
          </div>

          <div className="grid gap-3 md:grid-cols-2">
            <Select
              data={executorOptions}
              error={form.errors.executor_id}
              label="Ответственный исполнитель"
              placeholder="Выберите исполнителя"
              value={form.values.executor_id || null}
              onChange={(value) => form.setFieldValue("executor_id", value ?? "")}
            />
            <Select
              data={workStatusOptions.map((status) => ({ label: status.label, value: status.value }))}
              label="Статус"
              value={form.values.status}
              onChange={(value) => form.setFieldValue("status", value ?? "new")}
            />
          </div>

          <div className="grid gap-3 md:grid-cols-2">
            <TextInput
              disabled={naradContextLocked}
              label="Дата приема"
              type="datetime-local"
              {...form.getInputProps("received_at")}
            />
            <TextInput
              disabled={naradContextLocked}
              label="Дедлайн"
              type="datetime-local"
              {...form.getInputProps("deadline_at")}
            />
          </div>

          <div className="grid gap-3 md:grid-cols-3 xl:grid-cols-6">
            <TextInput
              label="Базовая цена"
              readOnly={selectedCatalogLocked}
              styles={priceFieldStyles}
              type="number"
              {...form.getInputProps("base_price_for_client")}
            />
            <div className="flex flex-col gap-1">
              <TextInput
                label="Скидка / надбавка, %"
                styles={priceFieldStyles}
                type="number"
                {...form.getInputProps("price_adjustment_percent")}
              />
              <Text c="dimmed" lh={1.3} size="xs">
                Отрицательное значение уменьшает стоимость.
              </Text>
            </div>
            <TextInput label="Итоговая цена клиенту" readOnly styles={priceFieldStyles} value={finalPrice} />
            <TextInput
              label="Трудозатраты, часы"
              readOnly={selectedCatalogLocked}
              styles={priceFieldStyles}
              type="number"
              {...form.getInputProps("labor_hours")}
            />
            <TextInput
              label="Доп. расходы"
              styles={priceFieldStyles}
              type="number"
              {...form.getInputProps("additional_expenses")}
            />
          </div>
          <Text c="dimmed" size="sm">
            Ручные трудозатраты по часам используются только если операции ниже не заполнены.
          </Text>
          <Textarea
            label="Описание"
            minRows={3}
            readOnly={selectedCatalogLocked}
            {...form.getInputProps("description")}
          />

          <Divider />
          <Stack gap="sm">
            <Group justify="space-between" align="start">
              <div>
                <Text fw={700}>Дополнительные позиции заказа</Text>
                <Text c="dimmed" size="sm">
                  Основная позиция берется из верхних полей. Ниже можно добавить еще строки в тот же заказ.
                </Text>
              </div>
              <Button
                leftSection={<IconPlus size={16} />}
                type="button"
                variant="light"
                onClick={() =>
                  form.insertListItem("work_items", {
                    work_catalog_item_id: "",
                    work_type: "",
                    description: "",
                    quantity: "1",
                    unit_price: ""
                  })
                }
              >
                Добавить позицию
              </Button>
            </Group>

            {form.values.work_items.length ? (
              <Stack gap="sm">
                {form.errors.work_items ? (
                  <Text c="red" size="sm">
                    {form.errors.work_items}
                  </Text>
                ) : null}
                {form.values.work_items.map((item, index) => (
                  <div key={`work-item-${index}`} className="rounded-[20px] bg-slate-50 px-4 py-4">
                    <div className="grid gap-3 md:grid-cols-[1.4fr_1fr_.7fr_.8fr_auto] md:items-end">
                      <Select
                        data={workCatalogOptions}
                        label={`Позиция ${index + 2}`}
                        placeholder="Выберите работу из каталога"
                        searchable
                        value={item.work_catalog_item_id || null}
                        onChange={(value) => {
                          const nextItem = workCatalogById.get(value ?? "");
                          form.setFieldValue(`work_items.${index}.work_catalog_item_id`, value ?? "");
                          if (!nextItem) {
                            form.setFieldValue(`work_items.${index}.work_type`, "");
                            return;
                          }
                          const resolvedPrice = resolveCatalogPrice(
                            selectedClientDetailQuery.data,
                            nextItem.id,
                            nextItem.base_price
                          );
                          form.setFieldValue(`work_items.${index}.work_type`, nextItem.name);
                          form.setFieldValue(`work_items.${index}.description`, nextItem.description ?? "");
                          form.setFieldValue(`work_items.${index}.unit_price`, resolvedPrice.price);
                        }}
                      />
                      <TextInput
                        label="Наименование"
                        placeholder="Подставляется из позиции каталога"
                        readOnly
                        value={item.work_type}
                      />
                      <TextInput
                        label="Кол-во"
                        type="number"
                        value={item.quantity}
                        onChange={(event) =>
                          form.setFieldValue(`work_items.${index}.quantity`, event.currentTarget.value)
                        }
                      />
                      <TextInput
                        label="Цена за ед."
                        readOnly={Boolean(item.work_catalog_item_id)}
                        type="number"
                        value={item.unit_price}
                        onChange={(event) =>
                          form.setFieldValue(`work_items.${index}.unit_price`, event.currentTarget.value)
                        }
                      />
                      <ActionIcon
                        color="red"
                        mb={4}
                        mt="auto"
                        size="lg"
                        variant="light"
                        onClick={() => form.removeListItem("work_items", index)}
                      >
                        <IconTrash size={16} />
                      </ActionIcon>
                    </div>
                    <Textarea
                      className="mt-3"
                      label="Описание позиции"
                      minRows={2}
                      readOnly={Boolean(item.work_catalog_item_id)}
                      value={item.description}
                      onChange={(event) =>
                        form.setFieldValue(`work_items.${index}.description`, event.currentTarget.value)
                      }
                    />
                    <Text c="dimmed" mt="sm" size="sm">
                      Итог по строке:{" "}
                      {formatCurrency((Number(item.quantity || 0) || 0) * (Number(item.unit_price || 0) || 0))}
                    </Text>
                  </div>
                ))}
              </Stack>
            ) : (
              <Text c="dimmed" size="sm">
                Заказ можно оставить однострочным, а дополнительные позиции добавить позже.
              </Text>
            )}
          </Stack>

          <Divider />
          <Stack gap="sm">
            <Group justify="space-between" align="start">
              <div>
                <Text fw={700}>Операции в работе</Text>
                <Text c="dimmed" size="sm">
                  Подбирай операции из каталога. Если у исполнителя назначена категория оплаты, ставка подставится автоматически.
                </Text>
              </div>
              <Button
                leftSection={<IconPlus size={16} />}
                type="button"
                variant="light"
                onClick={() =>
                  form.insertListItem("operations", {
                    operation_id: "",
                    executor_id: "",
                    quantity: "1",
                    unit_labor_cost_override: "",
                    note: ""
                  })
                }
              >
                Добавить операцию
              </Button>
            </Group>

            {form.values.operations.length ? (
              <>
                <Text fw={600} size="sm">
                  Предварительная оплата технику: {formatCurrency(calculatedOperationsLabor)}
                </Text>
                <Stack gap="sm">
                  {form.values.operations.map((line, index) => {
                    const preview = operationLinesPreview[index];
                    const currentOperation = preview?.operation;

                    return (
                      <div key={`${line.operation_id}-${index}`} className="rounded-[20px] bg-slate-50 px-4 py-4">
                        <div className="grid gap-3 md:grid-cols-[1.4fr_1.2fr_.8fr_1fr_auto] md:items-end">
                          <Select
                            data={operationOptions}
                            label={`Операция ${index + 1}`}
                            placeholder="Выберите операцию"
                            value={line.operation_id || null}
                            onChange={(value) => {
                              const nextOperation = operationsById.get(value ?? "");
                              form.setFieldValue(`operations.${index}.operation_id`, value ?? "");
                              form.setFieldValue(`operations.${index}.quantity`, nextOperation?.default_quantity ?? "1");
                            }}
                          />
                          <Select
                            clearable
                            data={executorOptions}
                            label="Исполнитель операции"
                            placeholder={form.values.executor_id ? "По умолчанию из заказа" : "Опционально"}
                            value={line.executor_id || null}
                            onChange={(value) => form.setFieldValue(`operations.${index}.executor_id`, value ?? "")}
                          />
                          <TextInput
                            label="Количество"
                            type="number"
                            value={line.quantity}
                            onChange={(event) => form.setFieldValue(`operations.${index}.quantity`, event.currentTarget.value)}
                          />
                          <TextInput
                            label="Ручная ставка"
                            placeholder="Авто"
                            type="number"
                            value={line.unit_labor_cost_override}
                            onChange={(event) =>
                              form.setFieldValue(`operations.${index}.unit_labor_cost_override`, event.currentTarget.value)
                            }
                          />
                          <ActionIcon
                            color="red"
                            mb={4}
                            mt="auto"
                            size="lg"
                            variant="light"
                            onClick={() => form.removeListItem("operations", index)}
                          >
                            <IconTrash size={16} />
                          </ActionIcon>
                        </div>
                        <Textarea
                          className="mt-3"
                          label="Примечание по операции"
                          minRows={2}
                          value={line.note}
                          onChange={(event) => form.setFieldValue(`operations.${index}.note`, event.currentTarget.value)}
                        />
                        <Text c="dimmed" mt="sm" size="sm">
                          {currentOperation ? (
                            <>
                              Категория оплаты: {preview?.resolvedExecutor?.payment_category_name ?? "не назначена"} · ставка{" "}
                              {formatCurrency(preview?.resolvedRate ?? 0)} · итог {formatCurrency(preview?.total ?? 0)}
                            </>
                          ) : (
                            "Выберите операцию из каталога, чтобы увидеть расчет ставки."
                          )}
                        </Text>
                      </div>
                    );
                  })}
                </Stack>
              </>
            ) : (
              <Text c="dimmed" size="sm">
                Если добавить операции сейчас, работа сразу получит детализацию по этапам и автоматический расчет оплаты технику.
              </Text>
            )}
          </Stack>

          <Divider />
          <Group justify="space-between">
            <Text fw={700}>Материалы в работе</Text>
            <Button
              leftSection={<IconPlus size={16} />}
              type="button"
              variant="light"
              onClick={() => form.insertListItem("materials", { material_id: "", quantity: "1" })}
            >
              Добавить материал
            </Button>
          </Group>

          <Stack gap="sm">
            {form.values.materials.length ? (
              form.values.materials.map((line, index) => (
                <Group key={`${line.material_id}-${index}`} grow align="end">
                  <Select
                    data={materialOptions}
                    label={`Материал ${index + 1}`}
                    placeholder="Выберите материал"
                    value={line.material_id || null}
                    onChange={(value) => form.setFieldValue(`materials.${index}.material_id`, value ?? "")}
                  />
                  <TextInput
                    label="Количество"
                    type="number"
                    value={line.quantity}
                    onChange={(event) => form.setFieldValue(`materials.${index}.quantity`, event.currentTarget.value)}
                  />
                  <ActionIcon
                    color="red"
                    mb={4}
                    mt="auto"
                    size="lg"
                    variant="light"
                    onClick={() => form.removeListItem("materials", index)}
                  >
                    <IconTrash size={16} />
                  </ActionIcon>
                </Group>
              ))
            ) : (
              <Text c="dimmed" size="sm">
                Материалы можно не добавлять сразу, но калькулятор себестоимости будет точнее при заполнении.
              </Text>
            )}
          </Stack>

          <Group justify="flex-end">
            <Button color="gray" type="button" variant="light" onClick={onClose}>
              Отмена
            </Button>
            <Button loading={mutation.isPending} type="submit">
              Создать работу
            </Button>
          </Group>
        </Stack>
      </form>
    </Modal>
  );
}
