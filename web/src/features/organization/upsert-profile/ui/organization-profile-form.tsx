"use client";

import {
  Badge,
  Button,
  Group,
  Loader,
  MultiSelect,
  PasswordInput,
  Select,
  Stack,
  Switch,
  Text,
  Textarea,
  TextInput
} from "@mantine/core";
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
  payroll_period_start_days: string[];
  smtp_host: string;
  smtp_port: string;
  smtp_username: string;
  smtp_password: string;
  clear_smtp_password: boolean;
  smtp_from_email: string;
  smtp_from_name: string;
  smtp_reply_to: string;
  smtp_use_tls: boolean;
  smtp_use_ssl: boolean;
  comment: string;
};

const payrollPeriodOptions = Array.from({ length: 31 }, (_, index) => {
  const day = String(index + 1);
  return { value: day, label: day };
});

function optionalValue(value: string) {
  const normalized = value.trim();
  return normalized ? normalized : undefined;
}

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
      payroll_period_start_days: ["1"],
      smtp_host: "",
      smtp_port: "587",
      smtp_username: "",
      smtp_password: "",
      clear_smtp_password: false,
      smtp_from_email: "",
      smtp_from_name: "",
      smtp_reply_to: "",
      smtp_use_tls: true,
      smtp_use_ssl: false,
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
      payroll_period_start_days:
        profileQuery.data.payroll_period_start_days?.map((value) => String(value)) ?? ["1"],
      smtp_host: profileQuery.data.smtp_host ?? "",
      smtp_port: String(profileQuery.data.smtp_port ?? 587),
      smtp_username: profileQuery.data.smtp_username ?? "",
      smtp_password: "",
      clear_smtp_password: false,
      smtp_from_email: profileQuery.data.smtp_from_email ?? "",
      smtp_from_name: profileQuery.data.smtp_from_name ?? "",
      smtp_reply_to: profileQuery.data.smtp_reply_to ?? "",
      smtp_use_tls: profileQuery.data.smtp_use_tls ?? true,
      smtp_use_ssl: profileQuery.data.smtp_use_ssl ?? false,
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
      <form
        onSubmit={form.onSubmit((values) =>
          mutation.mutate({
            display_name: values.display_name.trim(),
            legal_name: values.legal_name.trim(),
            vat_mode: values.vat_mode,
            payroll_period_start_days: values.payroll_period_start_days
              .map((value) => Number.parseInt(value, 10))
              .filter((value) => Number.isInteger(value)),
            ...(optionalValue(values.short_name) ? { short_name: optionalValue(values.short_name) } : {}),
            ...(optionalValue(values.legal_address) ? { legal_address: optionalValue(values.legal_address) } : {}),
            ...(optionalValue(values.mailing_address) ? { mailing_address: optionalValue(values.mailing_address) } : {}),
            ...(optionalValue(values.phone) ? { phone: optionalValue(values.phone) } : {}),
            ...(optionalValue(values.email) ? { email: optionalValue(values.email) } : {}),
            ...(optionalValue(values.inn) ? { inn: optionalValue(values.inn) } : {}),
            ...(optionalValue(values.kpp) ? { kpp: optionalValue(values.kpp) } : {}),
            ...(optionalValue(values.ogrn) ? { ogrn: optionalValue(values.ogrn) } : {}),
            ...(optionalValue(values.bank_name) ? { bank_name: optionalValue(values.bank_name) } : {}),
            ...(optionalValue(values.bik) ? { bik: optionalValue(values.bik) } : {}),
            ...(optionalValue(values.settlement_account)
              ? { settlement_account: optionalValue(values.settlement_account) }
              : {}),
            ...(optionalValue(values.correspondent_account)
              ? { correspondent_account: optionalValue(values.correspondent_account) }
              : {}),
            ...(optionalValue(values.recipient_name) ? { recipient_name: optionalValue(values.recipient_name) } : {}),
            ...(optionalValue(values.director_name) ? { director_name: optionalValue(values.director_name) } : {}),
            ...(optionalValue(values.accountant_name) ? { accountant_name: optionalValue(values.accountant_name) } : {}),
            ...(optionalValue(values.smtp_host) ? { smtp_host: optionalValue(values.smtp_host) } : {}),
            smtp_port: Number.parseInt(values.smtp_port, 10) || 587,
            ...(optionalValue(values.smtp_username) ? { smtp_username: optionalValue(values.smtp_username) } : {}),
            ...(values.smtp_password.trim() ? { smtp_password: values.smtp_password } : {}),
            ...(optionalValue(values.smtp_from_email)
              ? { smtp_from_email: optionalValue(values.smtp_from_email) }
              : {}),
            ...(optionalValue(values.smtp_from_name) ? { smtp_from_name: optionalValue(values.smtp_from_name) } : {}),
            ...(optionalValue(values.smtp_reply_to) ? { smtp_reply_to: optionalValue(values.smtp_reply_to) } : {}),
            clear_smtp_password: values.clear_smtp_password,
            smtp_use_tls: values.smtp_use_tls,
            smtp_use_ssl: values.smtp_use_ssl,
            ...(optionalValue(values.comment) ? { comment: optionalValue(values.comment) } : {})
          })
        )}
      >
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
          <div>
            <MultiSelect
              label="Начало расчетных периодов ЗП"
              description="Дни месяца, с которых автоматически начинается новый период начисления."
              data={payrollPeriodOptions}
              searchable
              clearable={false}
              {...form.getInputProps("payroll_period_start_days")}
            />
            {profileQuery.data?.payroll_periods_preview?.length ? (
              <Group gap="xs" mt="xs">
                {profileQuery.data.payroll_periods_preview.map((period) => (
                  <Badge
                    key={period.key}
                    color={period.is_current ? "teal" : "gray"}
                    radius="xl"
                    variant={period.is_current ? "filled" : "light"}
                  >
                    {period.label}
                  </Badge>
                ))}
              </Group>
            ) : null}
          </div>
          <div className="rounded-[20px] border border-slate-200 bg-slate-50/80 p-4">
            <Stack gap="md">
              <Group justify="space-between" align="center">
                <div>
                  <Text fw={700}>SMTP и почтовая отправка</Text>
                  <Text c="dimmed" size="sm">
                    Используется для отправки счетов и актов заказчикам по e-mail.
                  </Text>
                </div>
                <Group gap="xs">
                  {profileQuery.data?.smtp_password_configured ? (
                    <Badge color="teal" radius="xl" variant="light">
                      Пароль сохранен
                    </Badge>
                  ) : null}
                  {profileQuery.data?.smtp_enabled ? (
                    <Badge color="blue" radius="xl" variant="light">
                      SMTP настроен
                    </Badge>
                  ) : null}
                </Group>
              </Group>
              <div className="grid gap-3 md:grid-cols-3">
                <TextInput label="SMTP host" {...form.getInputProps("smtp_host")} />
                <TextInput label="SMTP port" type="number" {...form.getInputProps("smtp_port")} />
                <TextInput label="SMTP логин" {...form.getInputProps("smtp_username")} />
              </div>
              <div className="grid gap-3 md:grid-cols-2">
                <PasswordInput
                  label="Новый пароль SMTP"
                  placeholder={profileQuery.data?.smtp_password_configured ? "Оставь пустым, чтобы не менять" : ""}
                  {...form.getInputProps("smtp_password")}
                />
                <TextInput label="E-mail отправителя" {...form.getInputProps("smtp_from_email")} />
              </div>
              <div className="grid gap-3 md:grid-cols-2">
                <TextInput label="Имя отправителя" {...form.getInputProps("smtp_from_name")} />
                <TextInput label="Reply-To" {...form.getInputProps("smtp_reply_to")} />
              </div>
              <Group grow>
                <Switch
                  label="Использовать STARTTLS"
                  checked={form.values.smtp_use_tls}
                  onChange={(event) => form.setFieldValue("smtp_use_tls", event.currentTarget.checked)}
                />
                <Switch
                  label="Использовать SSL"
                  checked={form.values.smtp_use_ssl}
                  onChange={(event) => form.setFieldValue("smtp_use_ssl", event.currentTarget.checked)}
                />
                <Switch
                  label="Сбросить сохраненный пароль"
                  checked={form.values.clear_smtp_password}
                  onChange={(event) => form.setFieldValue("clear_smtp_password", event.currentTarget.checked)}
                />
              </Group>
            </Stack>
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
