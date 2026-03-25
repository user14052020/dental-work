"use client";

import { Button, Group, Modal, NumberInput, Select, Stack, Text, Textarea, TextInput } from "@mantine/core";
import { useForm } from "@mantine/form";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { IconPlus, IconTrash } from "@tabler/icons-react";

import { dashboardQueryKeys } from "@/entities/dashboard/model/query-keys";
import { createInventoryAdjustment } from "@/entities/inventory-adjustments/api/inventory-adjustments-api";
import { inventoryAdjustmentsQueryKeys } from "@/entities/inventory-adjustments/model/query-keys";
import { materialsQueryKeys } from "@/entities/materials/model/query-keys";
import { useMaterialsQuery } from "@/entities/materials/model/use-materials-query";
import { formatMaterialUnit } from "@/entities/materials/model/material-units";
import { showErrorNotification } from "@/shared/lib/notifications/show-error";
import { showSuccessNotification } from "@/shared/lib/notifications/show-success";

type InventoryAdjustmentFormValues = {
  adjustment_number: string;
  recorded_at: string;
  comment: string;
  items: Array<{
    material_id: string;
    actual_stock: string;
    comment: string;
  }>;
};

type InventoryAdjustmentFormModalProps = {
  opened: boolean;
  onClose: () => void;
};

function createEmptyItem() {
  return {
    material_id: "",
    actual_stock: "",
    comment: ""
  };
}

export function InventoryAdjustmentFormModal({ opened, onClose }: InventoryAdjustmentFormModalProps) {
  const queryClient = useQueryClient();
  const materialsQuery = useMaterialsQuery({ page: 1, page_size: 100 });
  const materials = materialsQuery.data?.items ?? [];
  const form = useForm<InventoryAdjustmentFormValues>({
    initialValues: {
      adjustment_number: "",
      recorded_at: new Date().toISOString().slice(0, 10),
      comment: "",
      items: [createEmptyItem()]
    }
  });

  const mutation = useMutation({
    mutationFn: () =>
      createInventoryAdjustment({
        adjustment_number: form.values.adjustment_number,
        recorded_at: new Date(form.values.recorded_at).toISOString(),
        comment: form.values.comment || undefined,
        items: form.values.items.map((item) => ({
          material_id: item.material_id,
          actual_stock: item.actual_stock,
          comment: item.comment || undefined
        }))
      }),
    onSuccess() {
      queryClient.invalidateQueries({ queryKey: inventoryAdjustmentsQueryKeys.root });
      queryClient.invalidateQueries({ queryKey: materialsQueryKeys.root });
      queryClient.invalidateQueries({ queryKey: dashboardQueryKeys.root });
      showSuccessNotification("Инвентаризация сохранена.");
      form.reset();
      form.setFieldValue("recorded_at", new Date().toISOString().slice(0, 10));
      form.setFieldValue("items", [createEmptyItem()]);
      onClose();
    },
    onError(error) {
      showErrorNotification(error, "Не удалось сохранить инвентаризацию.");
    }
  });

  return (
    <Modal opened={opened} onClose={onClose} title="Новая инвентаризация" size="xl">
      <form
        onSubmit={form.onSubmit(() => {
          mutation.mutate();
        })}
      >
        <Stack gap="md">
          <Group grow>
            <TextInput label="Номер инвентаризации" required {...form.getInputProps("adjustment_number")} />
            <TextInput label="Дата пересчета" type="date" required {...form.getInputProps("recorded_at")} />
          </Group>

          <Textarea label="Комментарий к документу" minRows={2} {...form.getInputProps("comment")} />

          <Stack gap="sm">
            {form.values.items.map((item, index) => {
              const selectedMaterial = materials.find((material) => material.id === item.material_id);
              const expectedStock = selectedMaterial?.stock ?? "—";
              const delta =
                selectedMaterial && item.actual_stock
                  ? (Number(item.actual_stock) - Number(selectedMaterial.stock)).toFixed(3)
                  : "—";

              return (
                <div key={index} className="rounded-[20px] bg-slate-50 px-4 py-4">
                  <Group align="end" wrap="wrap">
                    <Select
                      className="min-w-[240px] flex-1"
                      data={materials.map((material) => ({
                        value: material.id,
                        label: material.name
                      }))}
                      label="Материал"
                      required
                      searchable
                      value={item.material_id || null}
                      onChange={(value) => {
                        const nextMaterial = materials.find((material) => material.id === value);
                        form.setFieldValue(`items.${index}.material_id`, value ?? "");
                        form.setFieldValue(`items.${index}.actual_stock`, nextMaterial?.stock ?? "");
                      }}
                    />
                    <TextInput
                      className="w-full md:w-[140px]"
                      label="Ожидалось"
                      value={expectedStock}
                      readOnly
                    />
                    <NumberInput
                      className="w-full md:w-[160px]"
                      decimalScale={3}
                      hideControls
                      label="Фактически"
                      min={0}
                      step={0.001}
                      value={item.actual_stock}
                      onChange={(value) => form.setFieldValue(`items.${index}.actual_stock`, String(value ?? ""))}
                    />
                    <TextInput
                      className="w-full md:w-[140px]"
                      label="Отклонение"
                      value={delta}
                      readOnly
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
                  {selectedMaterial ? (
                    <Text c="dimmed" size="sm" mt="xs">
                      Ед. изм.: {formatMaterialUnit(selectedMaterial.unit)} · Средняя цена: {selectedMaterial.average_price}
                    </Text>
                  ) : null}
                  <Textarea
                    label="Комментарий к строке"
                    minRows={2}
                    mt="sm"
                    {...form.getInputProps(`items.${index}.comment`)}
                  />
                </div>
              );
            })}
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
              Сохранить инвентаризацию
            </Button>
          </Group>
        </Stack>
      </form>
    </Modal>
  );
}
