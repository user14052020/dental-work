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

import { useClientsQuery } from "@/entities/clients/model/use-clients-query";
import { useExecutorsQuery } from "@/entities/executors/model/use-executors-query";
import { formatMaterialUnit } from "@/entities/materials/model/material-units";
import { useMaterialsQuery } from "@/entities/materials/model/use-materials-query";
import { createWork } from "@/entities/works/api/works-api";
import { worksQueryKeys } from "@/entities/works/model/query-keys";
import { workStatusOptions } from "@/entities/works/model/types";
import { toDateTimeLocal, toIsoDateTime } from "@/shared/lib/formatters/format-date";
import { showErrorNotification } from "@/shared/lib/notifications/show-error";
import { showSuccessNotification } from "@/shared/lib/notifications/show-success";

type MaterialLine = {
  material_id: string;
  quantity: string;
};

type WorkFormValues = {
  order_number: string;
  client_id: string;
  executor_id: string;
  work_type: string;
  description: string;
  status: string;
  received_at: string;
  deadline_at: string;
  price_for_client: string;
  additional_expenses: string;
  labor_hours: string;
  amount_paid: string;
  comment: string;
  materials: MaterialLine[];
};

const emptyValues: WorkFormValues = {
  order_number: "",
  client_id: "",
  executor_id: "",
  work_type: "",
  description: "",
  status: "new",
  received_at: toDateTimeLocal(new Date().toISOString()),
  deadline_at: "",
  price_for_client: "0",
  additional_expenses: "0",
  labor_hours: "0",
  amount_paid: "0",
  comment: "",
  materials: []
};

type WorkFormModalProps = {
  opened: boolean;
  onClose: () => void;
};

export function WorkFormModal({ opened, onClose }: WorkFormModalProps) {
  const queryClient = useQueryClient();
  const clientsQuery = useClientsQuery({ page: 1, page_size: 100 });
  const executorsQuery = useExecutorsQuery({ page: 1, page_size: 100 });
  const materialsQuery = useMaterialsQuery({ page: 1, page_size: 100 });
  const form = useForm<WorkFormValues>({
    initialValues: emptyValues,
    validate: {
      order_number: (value) => (value.trim().length >= 1 ? null : "Укажите номер заказа."),
      client_id: (value) => (value ? null : "Выберите клиента."),
      work_type: (value) => (value.trim().length >= 1 ? null : "Укажите тип работы.")
    }
  });

  const mutation = useMutation({
    mutationFn: () =>
      createWork({
        order_number: form.values.order_number,
        client_id: form.values.client_id,
        executor_id: form.values.executor_id || undefined,
        work_type: form.values.work_type,
        description: form.values.description || undefined,
        status: form.values.status as never,
        received_at: toIsoDateTime(form.values.received_at) as string,
        deadline_at: toIsoDateTime(form.values.deadline_at),
        price_for_client: form.values.price_for_client,
        additional_expenses: form.values.additional_expenses,
        labor_hours: form.values.labor_hours,
        amount_paid: form.values.amount_paid,
        comment: form.values.comment || undefined,
        materials: form.values.materials.filter((item) => item.material_id && Number(item.quantity) > 0)
      }),
    onSuccess() {
      queryClient.invalidateQueries({ queryKey: worksQueryKeys.root });
      showSuccessNotification("Работа создана.");
      form.setValues(emptyValues);
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

  return (
    <Modal opened={opened} onClose={onClose} size="xl" title="Новая работа">
      <form
        onSubmit={form.onSubmit(() => {
          mutation.mutate();
        })}
      >
        <Stack gap="md">
          <Group grow>
            <TextInput label="Номер заказа" {...form.getInputProps("order_number")} />
            <TextInput label="Тип работы" {...form.getInputProps("work_type")} />
          </Group>
          <Group grow align="start">
            <Select
              data={clientsQuery.data?.items.map((client) => ({ value: client.id, label: client.name })) ?? []}
              label="Клиент"
              placeholder="Выберите клиента"
              value={form.values.client_id || null}
              onChange={(value) => form.setFieldValue("client_id", value ?? "")}
            />
            <Select
              data={
                executorsQuery.data?.items.map((executor) => ({
                  value: executor.id,
                  label: executor.full_name
                })) ?? []
              }
              label="Исполнитель"
              placeholder="Опционально"
              value={form.values.executor_id || null}
              onChange={(value) => form.setFieldValue("executor_id", value ?? "")}
            />
            <Select
              data={workStatusOptions.map((status) => ({ label: status.label, value: status.value }))}
              label="Статус"
              value={form.values.status}
              onChange={(value) => form.setFieldValue("status", value ?? "new")}
            />
          </Group>
          <Group grow>
            <TextInput label="Дата приема" type="datetime-local" {...form.getInputProps("received_at")} />
            <TextInput label="Дедлайн" type="datetime-local" {...form.getInputProps("deadline_at")} />
          </Group>
          <Group grow>
            <TextInput label="Цена для клиента" type="number" {...form.getInputProps("price_for_client")} />
            <TextInput label="Трудозатраты, часы" type="number" {...form.getInputProps("labor_hours")} />
            <TextInput label="Доп. расходы" type="number" {...form.getInputProps("additional_expenses")} />
            <TextInput label="Оплачено" type="number" {...form.getInputProps("amount_paid")} />
          </Group>
          <Textarea label="Описание" minRows={3} {...form.getInputProps("description")} />
          <Textarea label="Комментарий" minRows={2} {...form.getInputProps("comment")} />

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
                    onChange={(event) =>
                      form.setFieldValue(`materials.${index}.quantity`, event.currentTarget.value)
                    }
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
