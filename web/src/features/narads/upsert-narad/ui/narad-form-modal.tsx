"use client";

import { Button, Checkbox, Group, Modal, NumberInput, Select, Stack, Text, TextInput, Textarea } from "@mantine/core";
import { useForm } from "@mantine/form";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef } from "react";

import { useClientsQuery } from "@/entities/clients/model/use-clients-query";
import { useContractorsQuery } from "@/entities/contractors/model/use-contractors-query";
import { useDoctorsQuery } from "@/entities/doctors/model/use-doctors-query";
import { createNarad, updateNarad } from "@/entities/narads/api/narads-api";
import { naradsQueryKeys } from "@/entities/narads/model/query-keys";
import { Narad } from "@/entities/narads/model/types";
import { faceShapeOptions, patientGenderOptions } from "@/entities/works/model/types";
import { formatToothSelectionSummary, ToothSelectionItem } from "@/entities/works/model/tooth-selection";
import { Odontogram } from "@/entities/works/ui/odontogram";
import { worksQueryKeys } from "@/entities/works/model/query-keys";
import { toDateTimeLocal, toIsoDateTime } from "@/shared/lib/formatters/format-date";
import { showErrorNotification } from "@/shared/lib/notifications/show-error";
import { showSuccessNotification } from "@/shared/lib/notifications/show-success";

type NaradFormValues = {
  narad_number: string;
  client_id: string;
  doctor_id: string;
  title: string;
  description: string;
  doctor_name: string;
  doctor_phone: string;
  patient_name: string;
  patient_age: string;
  patient_gender: string;
  require_color_photo: boolean;
  face_shape: string;
  implant_system: string;
  metal_type: string;
  shade_color: string;
  tooth_formula: string;
  tooth_selection: ToothSelectionItem[];
  received_at: string;
  deadline_at: string;
  is_outside_work: boolean;
  contractor_id: string;
  outside_order_number: string;
  outside_cost: string;
  outside_sent_at: string;
  outside_due_at: string;
  outside_returned_at: string;
  outside_comment: string;
};

type NaradFormModalProps = {
  narad?: Narad | null;
  opened: boolean;
  onClose: () => void;
};

function buildInitialValues(narad?: Narad | null): NaradFormValues {
  if (!narad) {
    return {
      narad_number: "",
      client_id: "",
      doctor_id: "",
      title: "",
      description: "",
      doctor_name: "",
      doctor_phone: "",
      patient_name: "",
      patient_age: "",
      patient_gender: "",
      require_color_photo: false,
      face_shape: "",
      implant_system: "",
      metal_type: "",
      shade_color: "",
      tooth_formula: "",
      tooth_selection: [],
      received_at: toDateTimeLocal(new Date().toISOString()),
      deadline_at: "",
      is_outside_work: false,
      contractor_id: "",
      outside_order_number: "",
      outside_cost: "0",
      outside_sent_at: "",
      outside_due_at: "",
      outside_returned_at: "",
      outside_comment: ""
    };
  }

  return {
    narad_number: narad.narad_number,
    client_id: narad.client_id,
    doctor_id: narad.doctor_id ?? "",
    title: narad.title,
    description: narad.description ?? "",
    doctor_name: narad.doctor_name ?? "",
    doctor_phone: narad.doctor_phone ?? "",
    patient_name: narad.patient_name ?? "",
    patient_age: narad.patient_age !== null && narad.patient_age !== undefined ? String(narad.patient_age) : "",
    patient_gender: narad.patient_gender ?? "",
    require_color_photo: narad.require_color_photo,
    face_shape: narad.face_shape ?? "",
    implant_system: narad.implant_system ?? "",
    metal_type: narad.metal_type ?? "",
    shade_color: narad.shade_color ?? "",
    tooth_formula: narad.tooth_formula ?? "",
    tooth_selection: narad.tooth_selection ?? [],
    received_at: toDateTimeLocal(narad.received_at),
    deadline_at: toDateTimeLocal(narad.deadline_at),
    is_outside_work: narad.is_outside_work,
    contractor_id: narad.contractor_id ?? "",
    outside_order_number: narad.outside_order_number ?? "",
    outside_cost: narad.outside_cost ?? "0",
    outside_sent_at: toDateTimeLocal(narad.outside_sent_at),
    outside_due_at: toDateTimeLocal(narad.outside_due_at),
    outside_returned_at: toDateTimeLocal(narad.outside_returned_at),
    outside_comment: narad.outside_comment ?? ""
  };
}

export function NaradFormModal({ narad, opened, onClose }: NaradFormModalProps) {
  const queryClient = useQueryClient();
  const syncedNaradKeyRef = useRef<string | null>(null);
  const clientsQuery = useClientsQuery({ page: 1, page_size: 100 });
  const form = useForm<NaradFormValues>({
    initialValues: buildInitialValues(narad),
    validate: {
      narad_number: (value) => (value.trim() ? null : "Укажите номер наряда."),
      client_id: (value) => (value ? null : "Выберите клиента."),
      title: (value) => (value.trim() ? null : "Укажите заголовок наряда."),
      contractor_id: (value, values) => (values.is_outside_work && !value ? "Выберите подрядчика." : null),
      outside_sent_at: (value, values) =>
        values.is_outside_work && !value ? "Укажите дату отправки на сторону." : null
    }
  });
  const contractorsQuery = useContractorsQuery({
    page: 1,
    page_size: 100,
    active_only: true
  });
  const doctorsQuery = useDoctorsQuery({
    page: 1,
    page_size: 100,
    active_only: true,
    ...(form.values.client_id ? { client_id: form.values.client_id } : {})
  });

  useEffect(() => {
    if (!opened) {
      syncedNaradKeyRef.current = null;
      return;
    }

    const nextSyncKey = narad ? `${narad.id}:${narad.updated_at}` : "new";
    if (syncedNaradKeyRef.current === nextSyncKey) {
      return;
    }

    syncedNaradKeyRef.current = nextSyncKey;
    const nextValues = buildInitialValues(narad);
    form.setValues(nextValues);
    form.resetDirty(nextValues);
  }, [form, narad, opened]);

  const mutation = useMutation({
    mutationFn: () => {
      const payload = {
        narad_number: form.values.narad_number.trim(),
        client_id: form.values.client_id,
        doctor_id: form.values.doctor_id || null,
        title: form.values.title.trim(),
        description: form.values.description.trim() || null,
        doctor_name: form.values.doctor_name.trim() || null,
        doctor_phone: form.values.doctor_phone.trim() || null,
        patient_name: form.values.patient_name.trim() || null,
        patient_age: form.values.patient_age.trim() ? Number(form.values.patient_age) : null,
        patient_gender: form.values.patient_gender || null,
        require_color_photo: form.values.require_color_photo,
        face_shape: form.values.face_shape || null,
        implant_system: form.values.implant_system.trim() || null,
        metal_type: form.values.metal_type.trim() || null,
        shade_color: form.values.shade_color.trim() || null,
        tooth_formula: form.values.tooth_formula || null,
        tooth_selection: form.values.tooth_selection,
        received_at: toIsoDateTime(form.values.received_at) as string,
        deadline_at: form.values.deadline_at ? (toIsoDateTime(form.values.deadline_at) as string) : null,
        is_outside_work: form.values.is_outside_work,
        contractor_id: form.values.is_outside_work ? form.values.contractor_id || null : null,
        outside_order_number: form.values.is_outside_work ? form.values.outside_order_number.trim() || null : null,
        outside_cost: form.values.is_outside_work ? form.values.outside_cost || "0" : "0",
        outside_sent_at:
          form.values.is_outside_work && form.values.outside_sent_at
            ? (toIsoDateTime(form.values.outside_sent_at) as string)
            : null,
        outside_due_at:
          form.values.is_outside_work && form.values.outside_due_at
            ? (toIsoDateTime(form.values.outside_due_at) as string)
            : null,
        outside_returned_at:
          form.values.is_outside_work && form.values.outside_returned_at
            ? (toIsoDateTime(form.values.outside_returned_at) as string)
            : null,
        outside_comment: form.values.is_outside_work ? form.values.outside_comment.trim() || null : null
      };

      return narad ? updateNarad(narad.id, payload) : createNarad(payload);
    },
    onSuccess() {
      queryClient.invalidateQueries({ queryKey: naradsQueryKeys.root });
      queryClient.invalidateQueries({ queryKey: worksQueryKeys.root });
      showSuccessNotification(narad ? "Наряд обновлен." : "Наряд создан.");
      onClose();
    },
    onError(error) {
      showErrorNotification(error, narad ? "Не удалось обновить наряд." : "Не удалось создать наряд.");
    }
  });

  const clientOptions = (clientsQuery.data?.items ?? []).map((client) => ({
    value: client.id,
    label: client.name
  }));
  const doctorOptions = (doctorsQuery.data?.items ?? []).map((doctor) => ({
    value: doctor.id,
    label: doctor.specialization ? `${doctor.full_name} · ${doctor.specialization}` : doctor.full_name
  }));
  const contractorOptions = (contractorsQuery.data?.items ?? []).map((contractor) => ({
    value: contractor.id,
    label: contractor.name
  }));
  const doctorLocked = Boolean(form.values.doctor_id);
  const selectedContractor =
    contractorsQuery.data?.items.find((item) => item.id === form.values.contractor_id) ?? null;

  return (
    <Modal opened={opened} onClose={onClose} size="lg" title={narad ? "Редактировать наряд" : "Новый наряд"}>
      <form onSubmit={form.onSubmit(() => mutation.mutate())}>
        <Stack gap="md">
          <div className="grid gap-3 md:grid-cols-2">
            <TextInput label="Номер наряда" {...form.getInputProps("narad_number")} />
            <Select
              data={clientOptions}
              label="Клиент"
              placeholder="Выберите клиента"
              value={form.values.client_id || null}
              onChange={(value) => {
                form.setFieldValue("client_id", value ?? "");
                form.setFieldValue("doctor_id", "");
              }}
            />
          </div>

          <div className="grid gap-3 md:grid-cols-2">
            <TextInput label="Заголовок наряда" {...form.getInputProps("title")} />
            <Select
              clearable
              data={doctorOptions}
              label="Врач из справочника"
              placeholder={form.values.client_id ? "Выберите врача" : "Сначала выберите клиента"}
              searchable
              value={form.values.doctor_id || null}
              onChange={(value) => {
                const doctor = doctorsQuery.data?.items.find((item) => item.id === value);
                form.setFieldValue("doctor_id", value ?? "");
                if (doctor) {
                  form.setFieldValue("doctor_name", doctor.full_name);
                  form.setFieldValue("doctor_phone", doctor.phone ?? "");
                }
              }}
            />
          </div>

          <Textarea label="Описание" minRows={3} {...form.getInputProps("description")} />

          <div className="grid gap-3 md:grid-cols-2">
            <TextInput
              label="ФИО врача"
              readOnly={doctorLocked}
              {...form.getInputProps("doctor_name")}
            />
            <TextInput
              label="Телефон врача"
              readOnly={doctorLocked}
              {...form.getInputProps("doctor_phone")}
            />
          </div>

          <div className="grid gap-3 md:grid-cols-3">
            <TextInput label="Пациент" {...form.getInputProps("patient_name")} />
            <TextInput label="Возраст пациента" type="number" {...form.getInputProps("patient_age")} />
            <Select
              clearable
              data={patientGenderOptions}
              label="Пол пациента"
              value={form.values.patient_gender || null}
              onChange={(value) => form.setFieldValue("patient_gender", value ?? "")}
            />
          </div>

          <div className="grid gap-3 md:grid-cols-4">
            <Select
              clearable
              data={faceShapeOptions}
              label="Форма лица"
              value={form.values.face_shape || null}
              onChange={(value) => form.setFieldValue("face_shape", value ?? "")}
            />
            <TextInput label="Система имплантов" {...form.getInputProps("implant_system")} />
            <TextInput label="Металл" {...form.getInputProps("metal_type")} />
            <TextInput label="Цвет" {...form.getInputProps("shade_color")} />
          </div>

          <Checkbox
            label="Нужна отметка о фотоаппарате для определения цвета"
            {...form.getInputProps("require_color_photo", { type: "checkbox" })}
          />

          <Stack gap="xs">
            <Group justify="space-between" gap="sm" wrap="wrap">
              <Text fw={700}>Графическая зубная формула</Text>
              <Text c="dimmed" size="sm">
                {form.values.tooth_selection.length
                  ? `${form.values.tooth_selection.length} зуб(ов) отмечено`
                  : "Выбери зубы на схеме"}
              </Text>
            </Group>
            <Odontogram
              value={form.values.tooth_selection}
              onChange={(value) => {
                form.setFieldValue("tooth_selection", value);
                form.setFieldValue("tooth_formula", formatToothSelectionSummary(value));
              }}
            />
            <TextInput
              label="Сводка по формуле"
              placeholder="Формула сформируется автоматически"
              readOnly
              value={form.values.tooth_formula}
            />
          </Stack>

          <div className="grid gap-3 md:grid-cols-2">
            <TextInput label="Дата приема" type="datetime-local" {...form.getInputProps("received_at")} />
            <TextInput label="Дедлайн" type="datetime-local" {...form.getInputProps("deadline_at")} />
          </div>

          <Checkbox
            label="Работа выполняется на стороне / у подрядчика"
            {...form.getInputProps("is_outside_work", { type: "checkbox" })}
            onChange={(event) => {
              const checked = event.currentTarget.checked;
              form.setFieldValue("is_outside_work", checked);
              if (!checked) {
                form.setFieldValue("contractor_id", "");
                form.setFieldValue("outside_order_number", "");
                form.setFieldValue("outside_cost", "0");
                form.setFieldValue("outside_sent_at", "");
                form.setFieldValue("outside_due_at", "");
                form.setFieldValue("outside_returned_at", "");
                form.setFieldValue("outside_comment", "");
              }
            }}
          />

          {form.values.is_outside_work ? (
            <Stack gap="md" className="rounded-[20px] border border-slate-200 bg-slate-50/80 px-4 py-4">
              <Text fw={700}>Работа на стороне</Text>
              <div className="grid gap-3 md:grid-cols-2">
                <Select
                  data={contractorOptions}
                  label="Подрядчик"
                  placeholder="Выберите подрядчика"
                  searchable
                  value={form.values.contractor_id || null}
                  onChange={(value) => form.setFieldValue("contractor_id", value ?? "")}
                />
                <TextInput label="Внешний номер" {...form.getInputProps("outside_order_number")} />
              </div>
              <div className="grid gap-3 md:grid-cols-2">
                <TextInput label="Контактное лицо" readOnly value={selectedContractor?.contact_person ?? ""} />
                <TextInput label="Телефон подрядчика" readOnly value={selectedContractor?.phone ?? ""} />
              </div>
              <div className="grid gap-3 md:grid-cols-2">
                <NumberInput
                  label="Стоимость на стороне"
                  decimalScale={2}
                  hideControls
                  min={0}
                  step={0.01}
                  value={form.values.outside_cost}
                  onChange={(value) => form.setFieldValue("outside_cost", String(value ?? ""))}
                />
                <TextInput label="Дата отправки" type="datetime-local" {...form.getInputProps("outside_sent_at")} />
              </div>
              <div className="grid gap-3 md:grid-cols-2">
                <TextInput label="Вернуть до" type="datetime-local" {...form.getInputProps("outside_due_at")} />
                <TextInput
                  label="Дата возврата со стороны"
                  type="datetime-local"
                  {...form.getInputProps("outside_returned_at")}
                />
              </div>
              <Textarea label="Комментарий" minRows={2} {...form.getInputProps("outside_comment")} />
            </Stack>
          ) : null}

          <Group justify="flex-end">
            <Button color="gray" type="button" variant="light" onClick={onClose}>
              Отмена
            </Button>
            <Button loading={mutation.isPending} type="submit">
              {narad ? "Сохранить" : "Создать наряд"}
            </Button>
          </Group>
        </Stack>
      </form>
    </Modal>
  );
}
