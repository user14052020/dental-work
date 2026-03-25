"use client";

import { Button, Group, Modal, NumberInput, Select, Stack, Textarea, TextInput } from "@mantine/core";
import { useForm } from "@mantine/form";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { IconPlus, IconTrash } from "@tabler/icons-react";

import { createReceipt } from "@/entities/receipts/api/receipts-api";
import { receiptsQueryKeys } from "@/entities/receipts/model/query-keys";
import { useMaterialsQuery } from "@/entities/materials/model/use-materials-query";
import { materialsQueryKeys } from "@/entities/materials/model/query-keys";
import { dashboardQueryKeys } from "@/entities/dashboard/model/query-keys";
import { showErrorNotification } from "@/shared/lib/notifications/show-error";
import { showSuccessNotification } from "@/shared/lib/notifications/show-success";

type ReceiptFormValues = {
  receipt_number: string;
  received_at: string;
  supplier: string;
  comment: string;
  items: Array<{
    material_id: string;
    quantity: string;
    unit_price: string;
  }>;
};

type ReceiptFormModalProps = {
  opened: boolean;
  onClose: () => void;
};

function createEmptyItem() {
  return {
    material_id: "",
    quantity: "1",
    unit_price: "0"
  };
}

export function ReceiptFormModal({ opened, onClose }: ReceiptFormModalProps) {
  const queryClient = useQueryClient();
  const materialsQuery = useMaterialsQuery({ page: 1, page_size: 100 });
  const form = useForm<ReceiptFormValues>({
    initialValues: {
      receipt_number: "",
      received_at: new Date().toISOString().slice(0, 10),
      supplier: "",
      comment: "",
      items: [createEmptyItem()]
    }
  });

  const mutation = useMutation({
    mutationFn: () =>
      createReceipt({
        receipt_number: form.values.receipt_number,
        received_at: new Date(form.values.received_at).toISOString(),
        supplier: form.values.supplier || undefined,
        comment: form.values.comment || undefined,
        items: form.values.items.map((item) => ({
          material_id: item.material_id,
          quantity: item.quantity,
          unit_price: item.unit_price
        }))
      }),
    onSuccess() {
      queryClient.invalidateQueries({ queryKey: receiptsQueryKeys.root });
      queryClient.invalidateQueries({ queryKey: materialsQueryKeys.root });
      queryClient.invalidateQueries({ queryKey: dashboardQueryKeys.root });
      showSuccessNotification("Приход сохранён.");
      form.reset();
      form.setFieldValue("received_at", new Date().toISOString().slice(0, 10));
      form.setFieldValue("items", [createEmptyItem()]);
      onClose();
    },
    onError(error) {
      showErrorNotification(error, "Не удалось сохранить приход.");
    }
  });

  return (
    <Modal opened={opened} onClose={onClose} title="Новый приход" size="xl">
      <form
        onSubmit={form.onSubmit(() => {
          mutation.mutate();
        })}
      >
        <Stack gap="md">
          <Group grow>
            <TextInput label="Номер прихода" required {...form.getInputProps("receipt_number")} />
            <TextInput label="Дата поступления" type="date" required {...form.getInputProps("received_at")} />
            <TextInput label="Поставщик" {...form.getInputProps("supplier")} />
          </Group>

          <Textarea label="Комментарий" minRows={2} {...form.getInputProps("comment")} />

          <Stack gap="sm">
            {form.values.items.map((item, index) => (
              <div key={index} className="rounded-[20px] bg-slate-50 px-4 py-4">
                <Group align="end" wrap="wrap">
                  <Select
                    className="min-w-[240px] flex-1"
                    data={(materialsQuery.data?.items ?? []).map((material) => ({
                      value: material.id,
                      label: material.name
                    }))}
                    label="Материал"
                    required
                    searchable
                    value={item.material_id || null}
                    onChange={(value) => form.setFieldValue(`items.${index}.material_id`, value ?? "")}
                  />
                  <NumberInput
                    className="w-full md:w-[160px]"
                    decimalScale={3}
                    hideControls
                    label="Количество"
                    min={0.001}
                    step={0.001}
                    value={item.quantity}
                    onChange={(value) => form.setFieldValue(`items.${index}.quantity`, String(value ?? ""))}
                  />
                  <NumberInput
                    className="w-full md:w-[180px]"
                    decimalScale={2}
                    hideControls
                    label="Цена закупки"
                    min={0}
                    step={0.01}
                    value={item.unit_price}
                    onChange={(value) => form.setFieldValue(`items.${index}.unit_price`, String(value ?? ""))}
                  />
                  <Button
                    color="red"
                    variant="light"
                    leftSection={<IconTrash size={16} />}
                    disabled={form.values.items.length === 1}
                    onClick={() => form.removeListItem("items", index)}
                  >
                    Удалить
                  </Button>
                </Group>
              </div>
            ))}
            <Button
              variant="light"
              leftSection={<IconPlus size={16} />}
              onClick={() => form.insertListItem("items", createEmptyItem())}
            >
              Добавить строку
            </Button>
          </Stack>

          <Group justify="flex-end">
            <Button variant="default" onClick={onClose}>
              Отмена
            </Button>
            <Button type="submit" loading={mutation.isPending}>
              Сохранить приход
            </Button>
          </Group>
        </Stack>
      </form>
    </Modal>
  );
}
