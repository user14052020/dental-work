"use client";

import { Button, Group, Modal, Select, Stack, Textarea, TextInput } from "@mantine/core";
import { useForm } from "@mantine/form";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef } from "react";

import { createMaterial, updateMaterial } from "@/entities/materials/api/materials-api";
import { materialsQueryKeys } from "@/entities/materials/model/query-keys";
import {
  Material,
  MaterialCreatePayload,
  MaterialUpdatePayload
} from "@/entities/materials/model/types";
import { materialUnitOptions } from "@/entities/materials/model/material-units";
import { showErrorNotification } from "@/shared/lib/notifications/show-error";
import { showSuccessNotification } from "@/shared/lib/notifications/show-success";

type MaterialFormValues = {
  name: string;
  category: string;
  unit: string;
  stock: string;
  purchase_price: string;
  average_price: string;
  supplier: string;
  min_stock: string;
  comment: string;
};

const emptyValues: MaterialFormValues = {
  name: "",
  category: "",
  unit: "piece",
  stock: "0",
  purchase_price: "0",
  average_price: "0",
  supplier: "",
  min_stock: "0",
  comment: ""
};

function buildMaterialPayload(values: MaterialFormValues): MaterialCreatePayload {
  return {
    name: values.name.trim(),
    unit: values.unit.trim(),
    stock: values.stock,
    purchase_price: values.purchase_price,
    average_price: values.average_price,
    min_stock: values.min_stock,
    ...(values.category.trim() ? { category: values.category.trim() } : {}),
    ...(values.supplier.trim() ? { supplier: values.supplier.trim() } : {}),
    ...(values.comment.trim() ? { comment: values.comment.trim() } : {})
  };
}

function buildMaterialUpdatePayload(values: MaterialFormValues): MaterialUpdatePayload {
  return buildMaterialPayload(values);
}

type MaterialFormModalProps = {
  opened: boolean;
  onClose: () => void;
  material?: Material | null;
};

export function MaterialFormModal({ opened, onClose, material }: MaterialFormModalProps) {
  const queryClient = useQueryClient();
  const syncedMaterialKeyRef = useRef<string | null>(null);
  const form = useForm<MaterialFormValues>({
    initialValues: emptyValues,
    validate: {
      name: (value) => (value.trim().length >= 2 ? null : "Введите название материала."),
      unit: (value) => (value.trim().length >= 2 ? null : "Укажите единицу измерения.")
    }
  });

  useEffect(() => {
    if (!opened) {
      syncedMaterialKeyRef.current = null;
      return;
    }

    const nextSyncKey = material ? `${material.id}:${material.updated_at}` : "new";

    if (syncedMaterialKeyRef.current === nextSyncKey) {
      return;
    }

    syncedMaterialKeyRef.current = nextSyncKey;
    form.setValues(
      material
        ? {
            name: material.name,
            category: material.category ?? "",
            unit: material.unit,
            stock: material.stock,
            purchase_price: material.purchase_price,
            average_price: material.average_price,
            supplier: material.supplier ?? "",
            min_stock: material.min_stock,
            comment: material.comment ?? ""
          }
        : emptyValues
    );
  }, [form, material, opened]);

  const mutation = useMutation({
    mutationFn: async (values: MaterialFormValues) => {
      return material
        ? updateMaterial(material.id, buildMaterialUpdatePayload(values))
        : createMaterial(buildMaterialPayload(values));
    },
    onSuccess() {
      queryClient.invalidateQueries({ queryKey: materialsQueryKeys.root });
      showSuccessNotification(material ? "Материал обновлен." : "Материал добавлен.");
      onClose();
    },
    onError(error) {
      showErrorNotification(error, "Не удалось сохранить материал.");
    }
  });

  return (
    <Modal opened={opened} onClose={onClose} size="lg" title={material ? "Редактирование материала" : "Новый материал"}>
      <form onSubmit={form.onSubmit((values) => mutation.mutate(values))}>
        <Stack gap="md">
          <TextInput label="Название" {...form.getInputProps("name")} />
          <Group grow>
            <TextInput label="Категория" {...form.getInputProps("category")} />
            <Select
              data={materialUnitOptions.map((item) => ({ value: item.value, label: item.label }))}
              label="Единица измерения"
              value={form.values.unit}
              onChange={(value) => form.setFieldValue("unit", value ?? "piece")}
            />
          </Group>
          <Group grow>
            <TextInput label="Остаток" type="number" {...form.getInputProps("stock")} />
            <TextInput label="Минимальный остаток" type="number" {...form.getInputProps("min_stock")} />
          </Group>
          <Group grow>
            <TextInput label="Цена закупки" type="number" {...form.getInputProps("purchase_price")} />
            <TextInput label="Средняя цена" type="number" {...form.getInputProps("average_price")} />
          </Group>
          <TextInput label="Поставщик" {...form.getInputProps("supplier")} />
          <Textarea label="Комментарий" minRows={3} {...form.getInputProps("comment")} />
          <Group justify="flex-end">
            <Button color="gray" type="button" variant="light" onClick={onClose}>
              Отмена
            </Button>
            <Button loading={mutation.isPending} type="submit">
              {material ? "Сохранить" : "Создать"}
            </Button>
          </Group>
        </Stack>
      </form>
    </Modal>
  );
}
