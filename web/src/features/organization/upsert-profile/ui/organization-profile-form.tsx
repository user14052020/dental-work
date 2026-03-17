"use client";

import { Button, Group, Loader, Select, Stack, Text, Textarea, TextInput } from "@mantine/core";
import { useForm } from "@mantine/form";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef } from "react";

import { updateOrganizationProfile } from "@/entities/organization/api/organization-api";
import { organizationQueryKeys } from "@/entities/organization/model/query-keys";
import { useOrganizationProfileQuery } from "@/entities/organization/model/use-organization-query";
import { VatMode, vatOptions } from "@/shared/config/vat-options";
import { showErrorNotification } from "@/shared/lib/notifications/show-error";
import { showSuccessNotification } from "@/shared/lib/notifications/show-success";
import { SectionCard } from "@/shared/ui/section-card";

type OrganizationFormValues = {
  display_name: string;
  legal_name: string;
  short_name: string;
  legal_address: string;
  mailing_address: string;
  phone: string;
  email: string;
  inn: string;
  kpp: string;
  ogrn: string;
  bank_name: string;
  bik: string;
  settlement_account: string;
  correspondent_account: string;
  recipient_name: string;
  director_name: string;
  accountant_name: string;
  vat_mode: VatMode;
  comment: string;
};

export function OrganizationProfileForm() {
  const queryClient = useQueryClient();
  const profileQuery = useOrganizationProfileQuery();
  const syncedProfileKeyRef = useRef<string | null>(null);
  const form = useForm<OrganizationFormValues>({
    initialValues: {
      display_name: "",
      legal_name: "",
      short_name: "",
      legal_address: "",
      mailing_address: "",
      phone: "",
      email: "",
      inn: "",
      kpp: "",
      ogrn: "",
      bank_name: "",
      bik: "",
      settlement_account: "",
      correspondent_account: "",
      recipient_name: "",
      director_name: "",
      accountant_name: "",
      vat_mode: "without_vat",
      comment: ""
    },
    validate: {
      display_name: (value) => (value.trim().length >= 2 ? null : "Укажи название лаборатории."),
      legal_name: (value) => (value.trim().length >= 2 ? null : "Укажи юридическое название.")
    }
  });

  useEffect(() => {
    if (!profileQuery.data) {
      syncedProfileKeyRef.current = null;
      return;
    }

    const nextSyncKey = `${profileQuery.data.id}:${profileQuery.data.updated_at}`;
    if (syncedProfileKeyRef.current === nextSyncKey) {
      return;
    }

    syncedProfileKeyRef.current = nextSyncKey;
    form.setValues({
      display_name: profileQuery.data.display_name,
      legal_name: profileQuery.data.legal_name,
      short_name: profileQuery.data.short_name ?? "",
      legal_address: profileQuery.data.legal_address ?? "",
      mailing_address: profileQuery.data.mailing_address ?? "",
      phone: profileQuery.data.phone ?? "",
      email: profileQuery.data.email ?? "",
      inn: profileQuery.data.inn ?? "",
      kpp: profileQuery.data.kpp ?? "",
      ogrn: profileQuery.data.ogrn ?? "",
      bank_name: profileQuery.data.bank_name ?? "",
      bik: profileQuery.data.bik ?? "",
      settlement_account: profileQuery.data.settlement_account ?? "",
      correspondent_account: profileQuery.data.correspondent_account ?? "",
      recipient_name: profileQuery.data.recipient_name ?? "",
      director_name: profileQuery.data.director_name ?? "",
      accountant_name: profileQuery.data.accountant_name ?? "",
      vat_mode: profileQuery.data.vat_mode ?? "without_vat",
      comment: profileQuery.data.comment ?? ""
    });
  }, [form, profileQuery.data]);

  const mutation = useMutation({
    mutationFn: updateOrganizationProfile,
    onSuccess() {
      queryClient.invalidateQueries({ queryKey: organizationQueryKeys.root });
      showSuccessNotification("Профиль организации сохранен.");
    },
    onError(error) {
      showErrorNotification(error, "Не удалось сохранить профиль организации.");
    }
  });

  if (profileQuery.isLoading && !profileQuery.data) {
    return (
      <SectionCard>
        <Group justify="center" py="xl">
          <Loader />
        </Group>
      </SectionCard>
    );
  }

  return (
    <SectionCard>
      <form onSubmit={form.onSubmit((values) => mutation.mutate(values))}>
        <Stack gap="md">
          <div>
            <Text fw={700} size="lg">
              Реквизиты лаборатории
            </Text>
            <Text c="dimmed" size="sm">
              Эти данные используются в счете, акте и печатном наряде.
            </Text>
          </div>

          <div className="grid gap-3 md:grid-cols-2">
            <TextInput label="Название в интерфейсе" {...form.getInputProps("display_name")} />
            <TextInput label="Юридическое название" {...form.getInputProps("legal_name")} />
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            <TextInput label="Короткое название" {...form.getInputProps("short_name")} />
            <TextInput label="Получатель" {...form.getInputProps("recipient_name")} />
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            <TextInput label="Юридический адрес" {...form.getInputProps("legal_address")} />
            <TextInput label="Почтовый адрес" {...form.getInputProps("mailing_address")} />
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            <TextInput label="Телефон" {...form.getInputProps("phone")} />
            <TextInput label="Эл. почта" {...form.getInputProps("email")} />
          </div>
          <div className="grid gap-3 md:grid-cols-3">
            <TextInput label="ИНН" {...form.getInputProps("inn")} />
            <TextInput label="КПП" {...form.getInputProps("kpp")} />
            <TextInput label="ОГРН / ОГРНИП" {...form.getInputProps("ogrn")} />
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            <TextInput label="Банк" {...form.getInputProps("bank_name")} />
            <TextInput label="БИК" {...form.getInputProps("bik")} />
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            <TextInput label="Расчетный счет" {...form.getInputProps("settlement_account")} />
            <TextInput label="Корреспондентский счет" {...form.getInputProps("correspondent_account")} />
          </div>
          <div className="grid gap-3 md:grid-cols-3">
            <TextInput label="Руководитель" {...form.getInputProps("director_name")} />
            <TextInput label="Главный бухгалтер" {...form.getInputProps("accountant_name")} />
            <Select
              label="Режим НДС"
              data={vatOptions.map((option) => ({ value: option.value, label: option.label }))}
              {...form.getInputProps("vat_mode")}
            />
          </div>
          <Textarea label="Комментарий" minRows={3} {...form.getInputProps("comment")} />
          <Group justify="flex-end">
            <Button loading={mutation.isPending} type="submit">
              Сохранить реквизиты
            </Button>
          </Group>
        </Stack>
      </form>
    </SectionCard>
  );
}
