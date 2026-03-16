"use client";

import { Button, Group, Modal, Stack, TextInput } from "@mantine/core";
import { useForm } from "@mantine/form";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { consumeMaterial } from "@/entities/materials/api/materials-api";
import { materialsQueryKeys } from "@/entities/materials/model/query-keys";
import { showErrorNotification } from "@/shared/lib/notifications/show-error";
import { showSuccessNotification } from "@/shared/lib/notifications/show-success";

type ConsumeMaterialModalProps = {
  materialId?: string;
  opened: boolean;
  onClose: () => void;
};

export function ConsumeMaterialModal({ materialId, opened, onClose }: ConsumeMaterialModalProps) {
  const queryClient = useQueryClient();
  const form = useForm({
    initialValues: {
      quantity: "0"
    }
  });

  const mutation = useMutation({
    mutationFn: () => consumeMaterial(materialId as string, { quantity: form.values.quantity }),
    onSuccess() {
      queryClient.invalidateQueries({ queryKey: materialsQueryKeys.root });
      showSuccessNotification("Списание выполнено.");
      onClose();
      form.reset();
    },
    onError(error) {
      showErrorNotification(error, "Не удалось списать материал.");
    }
  });

  return (
    <Modal opened={opened} onClose={onClose} title="Списание материала">
      <form
        onSubmit={form.onSubmit(() => {
          mutation.mutate();
        })}
      >
        <Stack gap="md">
          <TextInput label="Количество" type="number" {...form.getInputProps("quantity")} />
          <Group justify="flex-end">
            <Button color="gray" type="button" variant="light" onClick={onClose}>
              Отмена
            </Button>
            <Button disabled={!materialId} loading={mutation.isPending} type="submit">
              Списать
            </Button>
          </Group>
        </Stack>
      </form>
    </Modal>
  );
}
