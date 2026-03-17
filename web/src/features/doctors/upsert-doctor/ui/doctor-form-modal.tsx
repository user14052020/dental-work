"use client";

import { Button, Checkbox, Modal, Select, Stack, TextInput, Textarea } from "@mantine/core";
import { useForm } from "@mantine/form";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef } from "react";

import { useClientsQuery } from "@/entities/clients/model/use-clients-query";
import { createDoctor, updateDoctor } from "@/entities/doctors/api/doctors-api";
import { doctorsQueryKeys } from "@/entities/doctors/model/query-keys";
import { Doctor, DoctorCreatePayload, DoctorUpdatePayload } from "@/entities/doctors/model/types";
import { showErrorNotification } from "@/shared/lib/notifications/show-error";
import { showSuccessNotification } from "@/shared/lib/notifications/show-success";

type DoctorFormValues = {
  client_id: string;
  full_name: string;
  phone: string;
  email: string;
  specialization: string;
  comment: string;
  is_active: boolean;
};

const emptyValues: DoctorFormValues = {
  client_id: "",
  full_name: "",
  phone: "",
  email: "",
  specialization: "",
  comment: "",
  is_active: true
};

function buildDoctorPayload(values: DoctorFormValues): DoctorCreatePayload {
  return {
    full_name: values.full_name.trim(),
    is_active: values.is_active,
    ...(values.client_id ? { client_id: values.client_id } : {}),
    ...(values.phone.trim() ? { phone: values.phone.trim() } : {}),
    ...(values.email.trim() ? { email: values.email.trim() } : {}),
    ...(values.specialization.trim() ? { specialization: values.specialization.trim() } : {}),
    ...(values.comment.trim() ? { comment: values.comment.trim() } : {})
  };
}

function buildDoctorUpdatePayload(values: DoctorFormValues): DoctorUpdatePayload {
  return buildDoctorPayload(values);
}

type DoctorFormModalProps = {
  doctor?: Doctor | null;
  opened: boolean;
  onClose: () => void;
};

export function DoctorFormModal({ doctor, opened, onClose }: DoctorFormModalProps) {
  const queryClient = useQueryClient();
  const clientsQuery = useClientsQuery({ page: 1, page_size: 100 });
  const syncedDoctorKeyRef = useRef<string | null>(null);
  const form = useForm<DoctorFormValues>({
    initialValues: emptyValues,
    validate: {
      full_name: (value) => (value.trim().length >= 2 ? null : "Укажите ФИО врача.")
    }
  });

  useEffect(() => {
    if (!opened) {
      syncedDoctorKeyRef.current = null;
      return;
    }

    const nextSyncKey = doctor ? `${doctor.id}:${doctor.updated_at}` : "new";
    if (syncedDoctorKeyRef.current === nextSyncKey) {
      return;
    }

    syncedDoctorKeyRef.current = nextSyncKey;
    form.setValues(
      doctor
        ? {
            client_id: doctor.client_id ?? "",
            full_name: doctor.full_name,
            phone: doctor.phone ?? "",
            email: doctor.email ?? "",
            specialization: doctor.specialization ?? "",
            comment: doctor.comment ?? "",
            is_active: doctor.is_active
          }
        : emptyValues
    );
  }, [doctor, form, opened]);

  const mutation = useMutation({
    mutationFn: async (values: DoctorFormValues) =>
      doctor ? updateDoctor(doctor.id, buildDoctorUpdatePayload(values)) : createDoctor(buildDoctorPayload(values)),
    onSuccess() {
      queryClient.invalidateQueries({ queryKey: doctorsQueryKeys.root });
      showSuccessNotification(doctor ? "Карточка врача обновлена." : "Врач добавлен.");
      onClose();
    },
    onError(error) {
      showErrorNotification(error, "Не удалось сохранить врача.");
    }
  });

  const clientOptions =
    clientsQuery.data?.items.map((client) => ({
      value: client.id,
      label: client.name
    })) ?? [];

  return (
    <Modal opened={opened} onClose={onClose} size="lg" title={doctor ? "Редактирование врача" : "Новый врач"}>
      <form onSubmit={form.onSubmit((values) => mutation.mutate(values))}>
        <Stack gap="md">
          <Select
            clearable
            data={clientOptions}
            label="Клиент / клиника"
            placeholder="Связать с клиентом"
            value={form.values.client_id || null}
            onChange={(value) => form.setFieldValue("client_id", value ?? "")}
          />
          <div className="grid gap-3 md:grid-cols-2">
            <TextInput label="ФИО" {...form.getInputProps("full_name")} />
            <TextInput label="Специализация" {...form.getInputProps("specialization")} />
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            <TextInput label="Телефон" {...form.getInputProps("phone")} />
            <TextInput label="Email" {...form.getInputProps("email")} />
          </div>
          <Textarea label="Комментарий" minRows={3} {...form.getInputProps("comment")} />
          <Checkbox
            label="Врач активен"
            {...form.getInputProps("is_active", { type: "checkbox" })}
          />
          <Button loading={mutation.isPending} type="submit">
            {doctor ? "Сохранить" : "Создать"}
          </Button>
        </Stack>
      </form>
    </Modal>
  );
}
