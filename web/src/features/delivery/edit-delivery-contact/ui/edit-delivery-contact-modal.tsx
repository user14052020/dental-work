"use client";

import { Button, Group, Modal, Stack, Text, TextInput } from "@mantine/core";
import { useForm } from "@mantine/form";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef } from "react";

import { updateClient } from "@/entities/clients/api/clients-api";
import { clientsQueryKeys } from "@/entities/clients/model/query-keys";
import { DeliveryItem } from "@/entities/delivery/model/types";
import { deliveryQueryKeys } from "@/entities/delivery/model/query-keys";
import { naradsQueryKeys } from "@/entities/narads/model/query-keys";
import { showErrorNotification } from "@/shared/lib/notifications/show-error";
import { showSuccessNotification } from "@/shared/lib/notifications/show-success";

type DeliveryContactFormValues = {
  delivery_address: string;
  delivery_contact: string;
  delivery_phone: string;
};

type EditDeliveryContactModalProps = {
  item?: DeliveryItem | null;
  opened: boolean;
  onClose: () => void;
};

export function EditDeliveryContactModal({ item, opened, onClose }: EditDeliveryContactModalProps) {
  const queryClient = useQueryClient();
  const syncedItemKeyRef = useRef<string | null>(null);
  const form = useForm<DeliveryContactFormValues>({
    initialValues: {
      delivery_address: "",
      delivery_contact: "",
      delivery_phone: ""
    }
  });

  useEffect(() => {
    if (!opened) {
      syncedItemKeyRef.current = null;
      return;
    }

    const nextSyncKey = item ? `${item.client_id}:${item.updated_at}` : "new";
    if (syncedItemKeyRef.current === nextSyncKey) {
      return;
    }

    syncedItemKeyRef.current = nextSyncKey;
    const nextValues = {
      delivery_address: item?.delivery_address ?? "",
      delivery_contact: item?.delivery_contact ?? "",
      delivery_phone: item?.delivery_phone ?? ""
    };
    form.setValues(nextValues);
    form.resetDirty(nextValues);
  }, [form, item, opened]);

  const mutation = useMutation({
    mutationFn: async (values: DeliveryContactFormValues) => {
      if (!item) {
        throw new Error("Клиент для доставки не выбран.");
      }

      return updateClient(item.client_id, {
        delivery_address: values.delivery_address.trim() || undefined,
        delivery_contact: values.delivery_contact.trim() || undefined,
        delivery_phone: values.delivery_phone.trim() || undefined
      });
    },
    onSuccess() {
      queryClient.invalidateQueries({ queryKey: deliveryQueryKeys.root });
      queryClient.invalidateQueries({ queryKey: clientsQueryKeys.root });
      queryClient.invalidateQueries({ queryKey: naradsQueryKeys.root });
      showSuccessNotification("Данные доставки обновлены.");
      onClose();
    },
    onError(error) {
      showErrorNotification(error, "Не удалось обновить данные доставки.");
    }
  });

  return (
    <Modal opened={opened} onClose={onClose} centered title="Редактирование доставки">
      <form onSubmit={form.onSubmit((values) => mutation.mutate(values))}>
        <Stack gap="md">
          <Text c="dimmed" size="sm">
            Изменения применяются к карточке заказчика {item?.client_name ?? ""} и будут использоваться в доставке и
            печатном листе.
          </Text>
          <TextInput label="Адрес доставки" {...form.getInputProps("delivery_address")} />
          <TextInput label="Контакт" {...form.getInputProps("delivery_contact")} />
          <TextInput label="Телефон" {...form.getInputProps("delivery_phone")} />
          <Group justify="flex-end">
            <Button color="gray" variant="light" type="button" onClick={onClose}>
              Отмена
            </Button>
            <Button loading={mutation.isPending} type="submit">
              Сохранить
            </Button>
          </Group>
        </Stack>
      </form>
    </Modal>
  );
}
