"use client";

import { ActionIcon, Button, Divider, Group, Modal, Select, Stack, Text, Textarea, TextInput } from "@mantine/core";
import { useForm } from "@mantine/form";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef } from "react";
import { IconPlus, IconTrash } from "@tabler/icons-react";

import { createClient, updateClient } from "@/entities/clients/api/clients-api";
import { clientsQueryKeys } from "@/entities/clients/model/query-keys";
import { useClientDetailQuery } from "@/entities/clients/model/use-clients-query";
import {
  Client,
  ClientDetail,
  ClientCreatePayload,
  ClientUpdatePayload
} from "@/entities/clients/model/types";
import { useWorkCatalogQuery } from "@/entities/work-catalog/model/use-work-catalog-query";
import { showErrorNotification } from "@/shared/lib/notifications/show-error";
import { showSuccessNotification } from "@/shared/lib/notifications/show-success";

type ClientCatalogPriceLine = {
  work_catalog_item_id: string;
  price: string;
  comment: string;
};

type ClientFormValues = {
  name: string;
  legal_name: string;
  contact_person: string;
  phone: string;
  email: string;
  address: string;
  delivery_address: string;
  delivery_contact: string;
  delivery_phone: string;
  legal_address: string;
  inn: string;
  kpp: string;
  ogrn: string;
  bank_name: string;
  bik: string;
  settlement_account: string;
  correspondent_account: string;
  contract_number: string;
  contract_date: string;
  signer_name: string;
  default_price_adjustment_percent: string;
  comment: string;
  work_catalog_prices: ClientCatalogPriceLine[];
};

type ClientFormModalProps = {
  opened: boolean;
  onClose: () => void;
  client?: Client | null;
};

const emptyValues: ClientFormValues = {
  name: "",
  legal_name: "",
  contact_person: "",
  phone: "",
  email: "",
  address: "",
  delivery_address: "",
  delivery_contact: "",
  delivery_phone: "",
  legal_address: "",
  inn: "",
  kpp: "",
  ogrn: "",
  bank_name: "",
  bik: "",
  settlement_account: "",
  correspondent_account: "",
  contract_number: "",
  contract_date: "",
  signer_name: "",
  default_price_adjustment_percent: "0",
  comment: "",
  work_catalog_prices: []
};

function buildClientPayload(values: ClientFormValues): ClientCreatePayload {
  return {
    name: values.name.trim(),
    ...(values.legal_name.trim() ? { legal_name: values.legal_name.trim() } : {}),
    ...(values.contact_person.trim() ? { contact_person: values.contact_person.trim() } : {}),
    ...(values.phone.trim() ? { phone: values.phone.trim() } : {}),
    ...(values.email.trim() ? { email: values.email.trim() } : {}),
    ...(values.address.trim() ? { address: values.address.trim() } : {}),
    ...(values.delivery_address.trim() ? { delivery_address: values.delivery_address.trim() } : {}),
    ...(values.delivery_contact.trim() ? { delivery_contact: values.delivery_contact.trim() } : {}),
    ...(values.delivery_phone.trim() ? { delivery_phone: values.delivery_phone.trim() } : {}),
    ...(values.legal_address.trim() ? { legal_address: values.legal_address.trim() } : {}),
    ...(values.inn.trim() ? { inn: values.inn.trim() } : {}),
    ...(values.kpp.trim() ? { kpp: values.kpp.trim() } : {}),
    ...(values.ogrn.trim() ? { ogrn: values.ogrn.trim() } : {}),
    ...(values.bank_name.trim() ? { bank_name: values.bank_name.trim() } : {}),
    ...(values.bik.trim() ? { bik: values.bik.trim() } : {}),
    ...(values.settlement_account.trim() ? { settlement_account: values.settlement_account.trim() } : {}),
    ...(values.correspondent_account.trim()
      ? { correspondent_account: values.correspondent_account.trim() }
      : {}),
    ...(values.contract_number.trim() ? { contract_number: values.contract_number.trim() } : {}),
    ...(values.contract_date ? { contract_date: values.contract_date } : {}),
    ...(values.signer_name.trim() ? { signer_name: values.signer_name.trim() } : {}),
    default_price_adjustment_percent: values.default_price_adjustment_percent || "0",
    ...(values.comment.trim() ? { comment: values.comment.trim() } : {}),
    work_catalog_prices: values.work_catalog_prices
      .filter((item) => item.work_catalog_item_id && item.price.trim() !== "")
      .map((item) => ({
        work_catalog_item_id: item.work_catalog_item_id,
        price: item.price,
        ...(item.comment.trim() ? { comment: item.comment.trim() } : {})
      }))
  };
}

function buildClientUpdatePayload(values: ClientFormValues): ClientUpdatePayload {
  return buildClientPayload(values);
}

function getSourceClientCatalogPrices(sourceClient?: Client | ClientDetail | null): ClientDetail["work_catalog_prices"] {
  if (sourceClient && "work_catalog_prices" in sourceClient) {
    return sourceClient.work_catalog_prices;
  }

  return [];
}

export function ClientFormModal({ opened, onClose, client }: ClientFormModalProps) {
  const queryClient = useQueryClient();
  const syncedClientKeyRef = useRef<string | null>(null);
  const clientDetailQuery = useClientDetailQuery(client?.id);
  const workCatalogQuery = useWorkCatalogQuery({ page: 1, page_size: 100, active_only: true });
  const form = useForm<ClientFormValues>({
    initialValues: emptyValues,
    validate: {
      name: (value) => (value.trim().length >= 2 ? null : "Название должно быть не короче 2 символов.")
    }
  });

  const sourceClient = clientDetailQuery.data ?? client;
  const workCatalogOptions =
    workCatalogQuery.data?.items.map((item) => ({
      value: item.id,
      label: `${item.code} · ${item.name}`
    })) ?? [];

  useEffect(() => {
    if (!opened) {
      syncedClientKeyRef.current = null;
      return;
    }

    const nextSyncKey = sourceClient ? `${sourceClient.id}:${sourceClient.updated_at}` : "new";
    if (syncedClientKeyRef.current === nextSyncKey) {
      return;
    }

    syncedClientKeyRef.current = nextSyncKey;
    const sourceClientCatalogPrices = getSourceClientCatalogPrices(sourceClient);
    form.setValues(
      sourceClient
        ? {
            name: sourceClient.name,
            legal_name: sourceClient.legal_name ?? "",
            contact_person: sourceClient.contact_person ?? "",
            phone: sourceClient.phone ?? "",
            email: sourceClient.email ?? "",
            address: sourceClient.address ?? "",
            delivery_address: sourceClient.delivery_address ?? "",
            delivery_contact: sourceClient.delivery_contact ?? "",
            delivery_phone: sourceClient.delivery_phone ?? "",
            legal_address: sourceClient.legal_address ?? "",
            inn: sourceClient.inn ?? "",
            kpp: sourceClient.kpp ?? "",
            ogrn: sourceClient.ogrn ?? "",
            bank_name: sourceClient.bank_name ?? "",
            bik: sourceClient.bik ?? "",
            settlement_account: sourceClient.settlement_account ?? "",
            correspondent_account: sourceClient.correspondent_account ?? "",
            contract_number: sourceClient.contract_number ?? "",
            contract_date: sourceClient.contract_date ?? "",
            signer_name: sourceClient.signer_name ?? "",
            default_price_adjustment_percent: sourceClient.default_price_adjustment_percent,
            comment: sourceClient.comment ?? "",
            work_catalog_prices: sourceClientCatalogPrices.map((item) => ({
                work_catalog_item_id: item.work_catalog_item_id,
                price: item.price,
                comment: item.comment ?? ""
              }))
          }
        : emptyValues
    );
  }, [form, opened, sourceClient]);

  const mutation = useMutation({
    mutationFn: async (values: ClientFormValues) =>
      client ? updateClient(client.id, buildClientUpdatePayload(values)) : createClient(buildClientPayload(values)),
    onSuccess() {
      queryClient.invalidateQueries({ queryKey: clientsQueryKeys.root });
      showSuccessNotification(client ? "Карточка клиента обновлена." : "Клиент добавлен.");
      onClose();
      form.reset();
    },
    onError(error) {
      showErrorNotification(error, "Не удалось сохранить клиента.");
    }
  });

  return (
    <Modal opened={opened} onClose={onClose} title={client ? "Редактирование клиента" : "Новый клиент"} size="xl">
      <form onSubmit={form.onSubmit((values) => mutation.mutate(values))}>
        <Stack gap="md">
          <TextInput label="Название клиники / клиента" {...form.getInputProps("name")} />
          <TextInput label="Юридическое название" {...form.getInputProps("legal_name")} />
          <TextInput label="Контактное лицо" {...form.getInputProps("contact_person")} />
          <Group grow>
            <TextInput label="Телефон" {...form.getInputProps("phone")} />
            <TextInput label="Эл. почта" {...form.getInputProps("email")} />
          </Group>
          <Group grow>
            <TextInput label="Адрес" {...form.getInputProps("address")} />
            <TextInput label="Юридический адрес" {...form.getInputProps("legal_address")} />
          </Group>
          <Group grow>
            <TextInput label="Адрес доставки" {...form.getInputProps("delivery_address")} />
            <TextInput label="Контакт по доставке" {...form.getInputProps("delivery_contact")} />
          </Group>
          <TextInput label="Телефон для доставки" {...form.getInputProps("delivery_phone")} />
          <Group grow>
            <TextInput label="ИНН" {...form.getInputProps("inn")} />
            <TextInput label="КПП" {...form.getInputProps("kpp")} />
            <TextInput label="ОГРН" {...form.getInputProps("ogrn")} />
          </Group>
          <Group grow>
            <TextInput label="Банк" {...form.getInputProps("bank_name")} />
            <TextInput label="БИК" {...form.getInputProps("bik")} />
          </Group>
          <Group grow>
            <TextInput label="Расчетный счет" {...form.getInputProps("settlement_account")} />
            <TextInput label="Корреспондентский счет" {...form.getInputProps("correspondent_account")} />
          </Group>
          <Group grow>
            <TextInput label="Номер договора" {...form.getInputProps("contract_number")} />
            <TextInput label="Дата договора" type="date" {...form.getInputProps("contract_date")} />
          </Group>
          <TextInput label="Подписант заказчика" {...form.getInputProps("signer_name")} />
          <TextInput
            label="Индивидуальная скидка / надбавка, %"
            description="Отрицательное значение — скидка, положительное — надбавка."
            type="number"
            {...form.getInputProps("default_price_adjustment_percent")}
          />
          <Divider />
          <Stack gap="sm">
            <Group justify="space-between" align="start">
              <div>
                <Text fw={700}>Индивидуальные цены по каталогу работ</Text>
                <Text c="dimmed" size="sm">
                  Эти цены имеют приоритет над общей ценой позиции каталога при создании работы.
                </Text>
              </div>
              <Button
                leftSection={<IconPlus size={16} />}
                type="button"
                variant="light"
                onClick={() =>
                  form.insertListItem("work_catalog_prices", {
                    work_catalog_item_id: "",
                    price: "",
                    comment: ""
                  })
                }
              >
                Добавить цену
              </Button>
            </Group>
            {form.values.work_catalog_prices.length ? (
              <Stack gap="sm">
                {form.values.work_catalog_prices.map((item, index) => (
                  <div key={`${item.work_catalog_item_id}-${index}`} className="rounded-[20px] bg-slate-50 px-4 py-4">
                    <div className="grid gap-3 md:grid-cols-[1.4fr_0.8fr_auto] md:items-end">
                      <Select
                        data={workCatalogOptions}
                        label={`Позиция каталога ${index + 1}`}
                        placeholder="Выберите работу"
                        value={item.work_catalog_item_id || null}
                        onChange={(value) =>
                          form.setFieldValue(`work_catalog_prices.${index}.work_catalog_item_id`, value ?? "")
                        }
                      />
                      <TextInput
                        label="Цена"
                        type="number"
                        value={item.price}
                        onChange={(event) =>
                          form.setFieldValue(`work_catalog_prices.${index}.price`, event.currentTarget.value)
                        }
                      />
                      <ActionIcon
                        color="red"
                        mb={4}
                        mt="auto"
                        size="lg"
                        variant="light"
                        onClick={() => form.removeListItem("work_catalog_prices", index)}
                      >
                        <IconTrash size={16} />
                      </ActionIcon>
                    </div>
                    <Textarea
                      className="mt-3"
                      label="Комментарий к цене"
                      minRows={2}
                      value={item.comment}
                      onChange={(event) =>
                        form.setFieldValue(`work_catalog_prices.${index}.comment`, event.currentTarget.value)
                      }
                    />
                  </div>
                ))}
              </Stack>
            ) : (
              <Text c="dimmed" size="sm">
                Если строки не добавлены, работа будет брать цену из общего каталога и стандартной скидки клиента.
              </Text>
            )}
          </Stack>
          <Textarea label="Комментарий" minRows={3} {...form.getInputProps("comment")} />
          <Group justify="flex-end">
            <Button color="gray" type="button" variant="light" onClick={onClose}>
              Отмена
            </Button>
            <Button loading={mutation.isPending} type="submit">
              {client ? "Сохранить изменения" : "Создать клиента"}
            </Button>
          </Group>
        </Stack>
      </form>
    </Modal>
  );
}
