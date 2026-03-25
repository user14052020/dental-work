"use client";

import { Badge, Button, Checkbox, Group, Modal, Select, Stack, Text, TextInput } from "@mantine/core";
import { useForm } from "@mantine/form";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useRef } from "react";

import { createEmployee, updateEmployee } from "@/entities/employees/api/employees-api";
import { useAuthSession } from "@/entities/auth/model/auth-session-context";
import { employeesQueryKeys } from "@/entities/employees/model/query-keys";
import {
  Employee,
  EmployeeCreatePayload,
  EmployeeUpdatePayload
} from "@/entities/employees/model/types";
import { useExecutorsQuery } from "@/entities/executors/model/use-executors-query";
import { employeePermissionGroups } from "@/shared/config/employee-permissions";
import { hasPermission } from "@/shared/lib/auth/permissions";
import { showErrorNotification } from "@/shared/lib/notifications/show-error";
import { showSuccessNotification } from "@/shared/lib/notifications/show-success";

type EmployeeFormValues = {
  full_name: string;
  email: string;
  phone: string;
  job_title: string;
  password: string;
  executor_id: string;
  permission_codes: string[];
  is_active: boolean;
  is_fired: boolean;
};

const emptyValues: EmployeeFormValues = {
  full_name: "",
  email: "",
  phone: "",
  job_title: "",
  password: "",
  executor_id: "",
  permission_codes: [],
  is_active: true,
  is_fired: false
};

function buildCreatePayload(values: EmployeeFormValues, canManagePermissions: boolean): EmployeeCreatePayload {
  return {
    full_name: values.full_name.trim(),
    email: values.email.trim(),
    password: values.password,
    is_active: values.is_active,
    is_fired: values.is_fired,
    ...(values.phone.trim() ? { phone: values.phone.trim() } : {}),
    ...(values.job_title.trim() ? { job_title: values.job_title.trim() } : {}),
    ...(values.executor_id ? { executor_id: values.executor_id } : {}),
    ...(canManagePermissions ? { permission_codes: values.permission_codes } : {})
  };
}

function buildUpdatePayload(values: EmployeeFormValues, canManagePermissions: boolean): EmployeeUpdatePayload {
  return {
    full_name: values.full_name.trim(),
    email: values.email.trim(),
    is_active: values.is_active,
    is_fired: values.is_fired,
    phone: values.phone.trim() || undefined,
    job_title: values.job_title.trim() || undefined,
    executor_id: values.executor_id || null,
    ...(canManagePermissions ? { permission_codes: values.permission_codes } : {}),
    ...(values.password ? { password: values.password } : {})
  };
}

type EmployeeFormModalProps = {
  opened: boolean;
  onClose: () => void;
  employee?: Employee | null;
};

export function EmployeeFormModal({ opened, onClose, employee }: EmployeeFormModalProps) {
  const queryClient = useQueryClient();
  const syncedEmployeeKeyRef = useRef<string | null>(null);
  const { session } = useAuthSession();
  const executorsQuery = useExecutorsQuery({
    page: 1,
    page_size: 100,
    active_only: true
  });
  const canManagePermissions = hasPermission(session?.user.permission_codes, "permissions.manage");
  const form = useForm<EmployeeFormValues>({
    initialValues: emptyValues,
    validate: {
      full_name: (value) => (value.trim().length >= 3 ? null : "Введите ФИО сотрудника."),
      email: (value) => (value.includes("@") ? null : "Введите e-mail."),
      password: (value, values) =>
        employee || value.length >= 8 ? null : "Для нового сотрудника нужен пароль минимум 8 символов."
    }
  });

  useEffect(() => {
    if (!opened) {
      syncedEmployeeKeyRef.current = null;
      return;
    }

    const nextSyncKey = employee ? `${employee.id}:${employee.updated_at}` : "new";
    if (syncedEmployeeKeyRef.current === nextSyncKey) {
      return;
    }

    syncedEmployeeKeyRef.current = nextSyncKey;
    form.setValues(
      employee
        ? {
            full_name: employee.full_name,
            email: employee.email,
            phone: employee.phone ?? "",
            job_title: employee.job_title ?? "",
            password: "",
            executor_id: employee.executor_id ?? "",
            permission_codes: employee.permission_codes ?? [],
            is_active: employee.is_active,
            is_fired: employee.is_fired
          }
        : emptyValues
    );
  }, [employee, form, opened]);

  const executorOptions = useMemo(
    () =>
      executorsQuery.data?.items.map((executor) => ({
        value: executor.id,
        label: `${executor.full_name}${executor.specialization ? ` · ${executor.specialization}` : ""}`
      })) ?? [],
    [executorsQuery.data?.items]
  );

  const mutation = useMutation({
    mutationFn: async (values: EmployeeFormValues) =>
      employee
        ? updateEmployee(employee.id, buildUpdatePayload(values, canManagePermissions))
        : createEmployee(buildCreatePayload(values, canManagePermissions)),
    onSuccess() {
      queryClient.invalidateQueries({ queryKey: employeesQueryKeys.root });
      showSuccessNotification(employee ? "Карточка сотрудника обновлена." : "Сотрудник добавлен.");
      onClose();
    },
    onError(error) {
      showErrorNotification(error, "Не удалось сохранить сотрудника.");
    }
  });

  return (
    <Modal opened={opened} onClose={onClose} size="xl" title={employee ? "Редактирование сотрудника" : "Новый сотрудник"}>
      <form onSubmit={form.onSubmit((values) => mutation.mutate(values))}>
        <Stack gap="md">
          <Group grow>
            <TextInput label="ФИО" {...form.getInputProps("full_name")} />
            <TextInput label="E-mail" {...form.getInputProps("email")} />
          </Group>
          <Group grow>
            <TextInput label="Телефон" {...form.getInputProps("phone")} />
            <TextInput label="Должность" {...form.getInputProps("job_title")} />
          </Group>
          <Group grow align="start">
            <TextInput
              label={employee ? "Новый пароль" : "Пароль"}
              placeholder={employee ? "Оставь пустым, чтобы не менять" : ""}
              {...form.getInputProps("password")}
            />
            <Select
              clearable
              searchable
              label="Техник-исполнитель"
              placeholder="Не привязывать"
              data={executorOptions}
              value={form.values.executor_id || null}
              onChange={(value) => form.setFieldValue("executor_id", value ?? "")}
            />
          </Group>

          {canManagePermissions ? (
            <Stack gap="xs">
              <Group justify="space-between" align="center">
                <Text fw={700}>Права доступа</Text>
                {form.values.permission_codes.includes("*") ? (
                  <Badge color="teal" radius="xl" variant="light">
                    Полный доступ
                  </Badge>
                ) : null}
              </Group>
              <Checkbox.Group
                value={form.values.permission_codes}
                onChange={(value) => form.setFieldValue("permission_codes", value)}
              >
                <Stack gap="md">
                  {employeePermissionGroups.map((group) => (
                    <Stack key={group.key} gap="xs">
                      <Text fw={600}>{group.label}</Text>
                      {group.items.map((permission) => (
                        <Checkbox
                          key={permission.code}
                          value={permission.code}
                          label={
                            <div>
                              <Text size="sm" fw={600}>
                                {permission.label}
                              </Text>
                              <Text c="dimmed" size="xs">
                                {permission.description}
                              </Text>
                            </div>
                          }
                        />
                      ))}
                    </Stack>
                  ))}
                </Stack>
              </Checkbox.Group>
            </Stack>
          ) : (
            <Stack gap={4}>
              <Text fw={700}>Права доступа</Text>
              <Text c="dimmed" size="sm">
                Изменение прав доступно только сотрудникам с разрешением на управление правами.
              </Text>
            </Stack>
          )}

          <Group grow>
            <Checkbox label="Активный аккаунт" {...form.getInputProps("is_active", { type: "checkbox" })} />
            <Checkbox label="Сотрудник уволен" {...form.getInputProps("is_fired", { type: "checkbox" })} />
          </Group>

          <Group justify="flex-end">
            <Button color="gray" variant="light" type="button" onClick={onClose}>
              Отмена
            </Button>
            <Button loading={mutation.isPending} type="submit">
              {employee ? "Сохранить" : "Создать"}
            </Button>
          </Group>
        </Stack>
      </form>
    </Modal>
  );
}
