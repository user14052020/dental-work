"use client";

import {
  ActionIcon,
  Button,
  Divider,
  Group,
  Select,
  Stack,
  Table,
  Text,
  TextInput
} from "@mantine/core";
import { useForm } from "@mantine/form";
import { useMutation } from "@tanstack/react-query";
import { IconPlus, IconTrash } from "@tabler/icons-react";

import { calculateCost } from "@/entities/cost-calculation/api/cost-calculation-api";
import { CostCalculationResult } from "@/entities/cost-calculation/model/types";
import { useExecutorsQuery } from "@/entities/executors/model/use-executors-query";
import { formatMaterialUnit } from "@/entities/materials/model/material-units";
import { useMaterialsQuery } from "@/entities/materials/model/use-materials-query";
import { formatCurrency } from "@/shared/lib/formatters/format-currency";
import { formatNumber } from "@/shared/lib/formatters/format-number";
import { showErrorNotification } from "@/shared/lib/notifications/show-error";
import { SectionCard } from "@/shared/ui/section-card";

type MaterialLine = {
  material_id: string;
  quantity: string;
  unit_cost_override: string;
};

type CostCalculatorValues = {
  executor_id: string;
  labor_hours: string;
  hourly_rate_override: string;
  additional_expenses: string;
  sale_price: string;
  materials: MaterialLine[];
};

type CostCalculatorFormProps = {
  result?: CostCalculationResult;
  onResult: (result: CostCalculationResult) => void;
};

export function CostCalculatorForm({ result, onResult }: CostCalculatorFormProps) {
  const materialsQuery = useMaterialsQuery({ page: 1, page_size: 100 });
  const executorsQuery = useExecutorsQuery({ page: 1, page_size: 100 });
  const form = useForm<CostCalculatorValues>({
    initialValues: {
      executor_id: "",
      labor_hours: "0",
      hourly_rate_override: "",
      additional_expenses: "0",
      sale_price: "0",
      materials: []
    }
  });

  const mutation = useMutation({
    mutationFn: () =>
      calculateCost({
        executor_id: form.values.executor_id || undefined,
        labor_hours: form.values.labor_hours,
        hourly_rate_override: form.values.hourly_rate_override || undefined,
        additional_expenses: form.values.additional_expenses,
        sale_price: form.values.sale_price,
        materials: form.values.materials
          .filter((line) => line.material_id && Number(line.quantity) > 0)
          .map((line) => ({
            material_id: line.material_id,
            quantity: line.quantity,
            unit_cost_override: line.unit_cost_override || undefined
          }))
      }),
    onSuccess(response) {
      onResult(response);
    },
    onError(error) {
      showErrorNotification(error, "Не удалось рассчитать себестоимость.");
    }
  });

  const materialOptions =
    materialsQuery.data?.items.map((material) => ({
      value: material.id,
      label: `${material.name} · ${formatMaterialUnit(material.unit)}`
    })) ?? [];

  return (
    <SectionCard>
      <form
        onSubmit={form.onSubmit(() => {
          mutation.mutate();
        })}
      >
        <Stack gap="lg">
          <div className="grid w-full gap-3 md:grid-cols-2 xl:grid-cols-5">
            <Select
              className="w-full"
              clearable
              data={
                executorsQuery.data?.items.map((executor) => ({
                  value: executor.id,
                  label: executor.full_name
                })) ?? []
              }
              label="Исполнитель"
              placeholder="Опционально"
              value={form.values.executor_id || null}
              onChange={(value) => form.setFieldValue("executor_id", value ?? "")}
            />
            <TextInput className="w-full" label="Трудозатраты, часы" type="number" {...form.getInputProps("labor_hours")} />
            <TextInput
              className="w-full"
              label="Ставка вручную"
              placeholder="Если нужно переопределить"
              type="number"
              {...form.getInputProps("hourly_rate_override")}
            />
            <TextInput className="w-full" label="Доп. расходы" type="number" {...form.getInputProps("additional_expenses")} />
            <TextInput className="w-full" label="Цена продажи" type="number" {...form.getInputProps("sale_price")} />
          </div>

          <Divider />
          <Group justify="space-between" className="flex-col items-start md:flex-row md:items-center">
            <Text fw={700}>Материалы</Text>
            <Button
              className="w-full md:w-auto"
              leftSection={<IconPlus size={16} />}
              type="button"
              variant="light"
              onClick={() =>
                form.insertListItem("materials", { material_id: "", quantity: "1", unit_cost_override: "" })
              }
            >
              Добавить строку
            </Button>
          </Group>

          <Stack gap="sm">
            {form.values.materials.length ? (
              form.values.materials.map((line, index) => (
                <div
                  key={`${line.material_id}-${index}`}
                  className="grid w-full gap-3 md:grid-cols-2 xl:grid-cols-[minmax(0,2fr)_minmax(0,1fr)_minmax(0,1fr)_auto]"
                >
                  <Select
                    className="w-full"
                    data={materialOptions}
                    label={`Материал ${index + 1}`}
                    value={line.material_id || null}
                    onChange={(value) => form.setFieldValue(`materials.${index}.material_id`, value ?? "")}
                  />
                  <TextInput
                    className="w-full"
                    label="Количество"
                    type="number"
                    value={line.quantity}
                    onChange={(event) =>
                      form.setFieldValue(`materials.${index}.quantity`, event.currentTarget.value)
                    }
                  />
                  <TextInput
                    className="w-full"
                    label="Цена вручную"
                    type="number"
                    value={line.unit_cost_override}
                    onChange={(event) =>
                      form.setFieldValue(`materials.${index}.unit_cost_override`, event.currentTarget.value)
                    }
                  />
                  <ActionIcon
                    color="red"
                    className="h-[42px] w-full self-end md:w-[42px]"
                    size="lg"
                    variant="light"
                    onClick={() => form.removeListItem("materials", index)}
                  >
                    <IconTrash size={16} />
                  </ActionIcon>
                </div>
              ))
            ) : (
              <Text c="dimmed" size="sm">
                Добавьте материалы, чтобы расчёт включал реальный расход.
              </Text>
            )}
          </Stack>

          <Group justify="flex-end">
            <Button className="w-full md:w-auto" loading={mutation.isPending} type="submit">
              Рассчитать
            </Button>
          </Group>
        </Stack>
      </form>

      {result ? (
        <>
          <Divider my="lg" />
          <Stack gap="md">
            <Text fw={700} size="lg">
              Результат расчёта
            </Text>
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <div className="rounded-[20px] bg-slate-50 p-5">
                <Text c="dimmed" size="sm">
                  Материалы
                </Text>
                <Text fw={800} mt={8} size="1.6rem">
                  {formatCurrency(result.materials_cost)}
                </Text>
              </div>
              <div className="rounded-[20px] bg-slate-50 p-5">
                <Text c="dimmed" size="sm">
                  Итоговая себестоимость
                </Text>
                <Text fw={800} mt={8} size="1.6rem">
                  {formatCurrency(result.total_cost)}
                </Text>
              </div>
              <div className="rounded-[20px] bg-slate-50 p-5">
                <Text c="dimmed" size="sm">
                  Маржинальность
                </Text>
                <Text fw={800} mt={8} size="1.6rem">
                  {formatNumber(result.profitability_percent)}%
                </Text>
              </div>
              <div className="rounded-[20px] bg-slate-50 p-5">
                <Text c="dimmed" size="sm">
                  Заработали
                </Text>
                <Text fw={800} mt={8} size="1.6rem">
                  {formatCurrency(result.margin)}
                </Text>
              </div>
            </div>

            {result.lines.length ? (
              <Table.ScrollContainer minWidth={760}>
                <Table verticalSpacing="md">
                  <Table.Thead>
                    <Table.Tr>
                      <Table.Th>Строка</Table.Th>
                      <Table.Th>Количество</Table.Th>
                      <Table.Th>Цена</Table.Th>
                      <Table.Th>Сумма</Table.Th>
                    </Table.Tr>
                  </Table.Thead>
                  <Table.Tbody>
                    {result.lines.map((line) => (
                      <Table.Tr key={`${line.name}-${line.quantity}`}>
                        <Table.Td>{line.name}</Table.Td>
                        <Table.Td>{line.quantity}</Table.Td>
                        <Table.Td>{formatCurrency(line.unit_cost)}</Table.Td>
                        <Table.Td>{formatCurrency(line.total_cost)}</Table.Td>
                      </Table.Tr>
                    ))}
                  </Table.Tbody>
                </Table>
              </Table.ScrollContainer>
            ) : null}
          </Stack>
        </>
      ) : null}
    </SectionCard>
  );
}
