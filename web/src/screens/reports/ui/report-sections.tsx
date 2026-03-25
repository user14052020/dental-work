"use client";

import { ActionIcon, Badge, Group, SimpleGrid, Table, Text, Tooltip } from "@mantine/core";
import {
  IconAlertTriangle,
  IconCoin,
  IconFiles,
  IconFlask2,
  IconPencil,
  IconReceipt2,
  IconStack2,
  IconTrash
} from "@tabler/icons-react";
import Link from "next/link";

import { ReportsSnapshot } from "@/entities/reports/model/types";
import { formatMaterialUnit } from "@/entities/materials/model/material-units";
import { reportDefinitions } from "@/screens/reports/ui/report-definitions";
import { formatCurrency } from "@/shared/lib/formatters/format-currency";
import { formatDateTime } from "@/shared/lib/formatters/format-date";
import { formatNumber } from "@/shared/lib/formatters/format-number";
import { KpiCard } from "@/shared/ui/kpi-card";
import { SectionCard } from "@/shared/ui/section-card";
import { StatusPill } from "@/shared/ui/status-pill";

export function ReportsOverviewCards({
  data,
  overdueHref
}: {
  data: ReportsSnapshot;
  overdueHref?: string;
}) {
  return (
    <SimpleGrid cols={{ base: 1, sm: 2, xl: 4 }} spacing="lg" verticalSpacing="lg">
      <KpiCard
        title="Наряды"
        value={String(data.summary.total_narads)}
        hint={`${data.summary.open_narads} открыто сейчас`}
        icon={<IconFiles size={26} />}
      />
      <KpiCard
        title="Просрочено"
        value={String(data.summary.overdue_narads)}
        hint="Наряды с истекшим сроком без закрытия"
        icon={<IconAlertTriangle size={26} />}
        href={overdueHref}
      />
      <KpiCard
        title="Выручка"
        value={formatCurrency(data.summary.total_revenue)}
        hint="Сумма работ за выбранный период"
        icon={<IconReceipt2 size={26} />}
      />
      <KpiCard
        title="К оплате"
        value={formatCurrency(data.summary.total_balance_due)}
        hint={`Получено ${formatCurrency(data.summary.total_paid)}`}
        icon={<IconCoin size={26} />}
      />
      <KpiCard
        title="ЗП техникам"
        value={formatCurrency(data.summary.payroll_total)}
        hint="Начислено по операциям в закрытых нарядах"
        icon={<IconStack2 size={26} />}
      />
      <KpiCard
        title="Расход по факту"
        value={formatCurrency(data.summary.actual_material_consumption_total)}
        hint="Ручные списания материалов без привязки к заказу"
        icon={<IconFlask2 size={26} />}
      />
    </SimpleGrid>
  );
}

export function ReportsCatalogSection() {
  return (
    <SimpleGrid cols={{ base: 1, md: 2, xl: 3 }} spacing="lg" verticalSpacing="lg">
      {reportDefinitions
        .filter((item) => item.href !== "/reports")
        .map((item) => (
          <Link key={item.href} href={item.href} className="no-underline">
            <SectionCard padding="xl">
              <Group justify="space-between" align="flex-start" wrap="nowrap">
                <div>
                  <Text fw={700} size="lg">
                    {item.title}
                  </Text>
                  <Text c="dimmed" size="sm" mt={6}>
                    {item.description}
                  </Text>
                </div>
                <item.icon size={24} />
              </Group>
            </SectionCard>
          </Link>
        ))}
    </SimpleGrid>
  );
}

export function ClientBalancesReportSection({ data }: { data: ReportsSnapshot }) {
  return (
    <SectionCard padding="xl">
      {data.client_balances.length ? (
        <Table.ScrollContainer minWidth={880}>
          <Table highlightOnHover verticalSpacing="md">
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Клиент</Table.Th>
                <Table.Th>Наряды</Table.Th>
                <Table.Th>Работы</Table.Th>
                <Table.Th>Сумма</Table.Th>
                <Table.Th>Оплачено</Table.Th>
                <Table.Th>Долг</Table.Th>
                <Table.Th>Последний заказ</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {data.client_balances.map((item) => (
                <Table.Tr key={item.client_id}>
                  <Table.Td>
                    <Text fw={700}>{item.client_name}</Text>
                  </Table.Td>
                  <Table.Td>{item.narads_count}</Table.Td>
                  <Table.Td>{item.works_count}</Table.Td>
                  <Table.Td>{formatCurrency(item.total_price)}</Table.Td>
                  <Table.Td>{formatCurrency(item.amount_paid)}</Table.Td>
                  <Table.Td>{formatCurrency(item.balance_due)}</Table.Td>
                  <Table.Td>{formatDateTime(item.last_received_at)}</Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </Table.ScrollContainer>
      ) : (
        <Text c="dimmed">По выбранному периоду нет клиентских данных.</Text>
      )}
    </SectionCard>
  );
}

export function ExecutorLoadReportSection({ data }: { data: ReportsSnapshot }) {
  return (
    <SectionCard padding="xl">
      {data.executors.length ? (
        <Table.ScrollContainer minWidth={820}>
          <Table highlightOnHover verticalSpacing="md">
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Исполнитель</Table.Th>
                <Table.Th>Активные</Table.Th>
                <Table.Th>Закрытые</Table.Th>
                <Table.Th>Выручка</Table.Th>
                <Table.Th>Начислено</Table.Th>
                <Table.Th>Последнее закрытие</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {data.executors.map((item) => (
                <Table.Tr key={item.executor_id}>
                  <Table.Td>
                    <Text fw={700}>{item.executor_name}</Text>
                  </Table.Td>
                  <Table.Td>{item.active_works}</Table.Td>
                  <Table.Td>{item.closed_works}</Table.Td>
                  <Table.Td>{formatCurrency(item.revenue_total)}</Table.Td>
                  <Table.Td>{formatCurrency(item.earnings_total)}</Table.Td>
                  <Table.Td>{formatDateTime(item.last_closed_at)}</Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </Table.ScrollContainer>
      ) : (
        <Text c="dimmed">По выбранному периоду нет данных по исполнителям.</Text>
      )}
    </SectionCard>
  );
}

export function PayrollReportSection({ data }: { data: ReportsSnapshot }) {
  return (
    <SectionCard padding="xl">
      {data.payroll.length ? (
        <Table.ScrollContainer minWidth={920}>
          <Table highlightOnHover verticalSpacing="md">
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Исполнитель</Table.Th>
                <Table.Th>Наряды</Table.Th>
                <Table.Th>Операции</Table.Th>
                <Table.Th>Количество</Table.Th>
                <Table.Th>Начислено</Table.Th>
                <Table.Th>Последнее закрытие</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {data.payroll.map((item) => (
                <Table.Tr key={item.executor_id}>
                  <Table.Td>
                    <Text fw={700}>{item.executor_name}</Text>
                  </Table.Td>
                  <Table.Td>{item.narads_count}</Table.Td>
                  <Table.Td>{item.operations_count}</Table.Td>
                  <Table.Td>{formatNumber(item.quantity_total)}</Table.Td>
                  <Table.Td>{formatCurrency(item.earnings_total)}</Table.Td>
                  <Table.Td>{formatDateTime(item.last_closed_at)}</Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </Table.ScrollContainer>
      ) : (
        <Text c="dimmed">По выбранному периоду начисления по техникам отсутствуют.</Text>
      )}
    </SectionCard>
  );
}

export function PayrollOperationsReportSection({ data }: { data: ReportsSnapshot }) {
  return (
    <SectionCard padding="xl">
      {data.payroll_operations.length ? (
        <Table.ScrollContainer minWidth={980}>
          <Table highlightOnHover verticalSpacing="md">
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Исполнитель</Table.Th>
                <Table.Th>Операция</Table.Th>
                <Table.Th>Наряды</Table.Th>
                <Table.Th>Строк</Table.Th>
                <Table.Th>Количество</Table.Th>
                <Table.Th>Начислено</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {data.payroll_operations.map((item) => (
                <Table.Tr key={`${item.executor_id}-${item.operation_code ?? item.operation_name}`}>
                  <Table.Td>
                    <Text fw={700}>{item.executor_name}</Text>
                  </Table.Td>
                  <Table.Td>
                    <Text fw={600}>{item.operation_name}</Text>
                    <Text c="dimmed" size="sm">
                      {item.operation_code ?? "Без кода"}
                    </Text>
                  </Table.Td>
                  <Table.Td>{item.narads_count}</Table.Td>
                  <Table.Td>{item.operations_count}</Table.Td>
                  <Table.Td>{formatNumber(item.quantity_total)}</Table.Td>
                  <Table.Td>{formatCurrency(item.earnings_total)}</Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </Table.ScrollContainer>
      ) : (
        <Text c="dimmed">Детализация по операциям за выбранный период отсутствует.</Text>
      )}
    </SectionCard>
  );
}

export function NaradsRegistryReportSection({ data }: { data: ReportsSnapshot }) {
  return (
    <SectionCard padding="xl">
      {data.narads.length ? (
        <Table.ScrollContainer minWidth={1240}>
          <Table highlightOnHover verticalSpacing="md">
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Наряд</Table.Th>
                <Table.Th>Статус</Table.Th>
                <Table.Th>Срок</Table.Th>
                <Table.Th>Работы</Table.Th>
                <Table.Th>Сумма</Table.Th>
                <Table.Th>Себестоимость</Table.Th>
                <Table.Th>Маржа</Table.Th>
                <Table.Th>Оплачено</Table.Th>
                <Table.Th>Долг</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {data.narads.map((item) => (
                <Table.Tr key={item.narad_id}>
                  <Table.Td>
                    <Text fw={700}>{item.narad_number}</Text>
                    <Text c="dimmed" size="sm">
                      {item.client_name} · {item.patient_name ?? item.doctor_name ?? item.title}
                    </Text>
                  </Table.Td>
                  <Table.Td>
                    <Group gap="xs">
                      <StatusPill value={item.status} />
                      {item.is_overdue ? (
                        <Badge color="red" radius="xl" variant="light">
                          Просрочен
                        </Badge>
                      ) : null}
                    </Group>
                  </Table.Td>
                  <Table.Td>{formatDateTime(item.deadline_at)}</Table.Td>
                  <Table.Td>{item.works_count}</Table.Td>
                  <Table.Td>{formatCurrency(item.total_price)}</Table.Td>
                  <Table.Td>{formatCurrency(item.total_cost)}</Table.Td>
                  <Table.Td>{formatCurrency(item.total_margin)}</Table.Td>
                  <Table.Td>{formatCurrency(item.amount_paid)}</Table.Td>
                  <Table.Td>{formatCurrency(item.balance_due)}</Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </Table.ScrollContainer>
      ) : (
        <Text c="dimmed">По выбранному периоду наряды не найдены.</Text>
      )}
    </SectionCard>
  );
}

export function MaterialStockReportSection({ data }: { data: ReportsSnapshot }) {
  return (
    <SectionCard padding="xl">
      {data.materials.length ? (
        <Table.ScrollContainer minWidth={1120}>
          <Table highlightOnHover verticalSpacing="md">
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Материал</Table.Th>
                <Table.Th>Остаток</Table.Th>
                <Table.Th>В резерве</Table.Th>
                <Table.Th>Доступно</Table.Th>
                <Table.Th>Мин.</Table.Th>
                <Table.Th>Стоимость</Table.Th>
                <Table.Th>Статус</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {data.materials.map((item) => (
                <Table.Tr key={item.material_id}>
                  <Table.Td>
                    <Text fw={700}>{item.name}</Text>
                    <Text c="dimmed" size="sm">
                      {item.category ?? "Без категории"} · {formatMaterialUnit(item.unit)}
                    </Text>
                  </Table.Td>
                  <Table.Td>{item.stock}</Table.Td>
                  <Table.Td>{item.reserved_stock}</Table.Td>
                  <Table.Td>{item.available_stock}</Table.Td>
                  <Table.Td>{item.min_stock}</Table.Td>
                  <Table.Td>{formatCurrency(item.stock_value)}</Table.Td>
                  <Table.Td>
                    <Badge color={item.is_low_stock ? "red" : "teal"} radius="xl" variant="light">
                      {item.is_low_stock ? "Низкий остаток" : "Норма"}
                    </Badge>
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </Table.ScrollContainer>
      ) : (
        <Text c="dimmed">Материалы для аналитики пока отсутствуют.</Text>
      )}
    </SectionCard>
  );
}

export function ActualMaterialConsumptionReportSection({
  data,
  onEdit,
  onDelete
}: {
  data: ReportsSnapshot;
  onEdit?: (movementId: string) => void;
  onDelete?: (movementId: string) => void;
}) {
  const canManage = Boolean(onEdit || onDelete);

  return (
    <SectionCard padding="xl">
      {data.actual_material_consumption.length ? (
        <Table.ScrollContainer minWidth={1140}>
          <Table highlightOnHover verticalSpacing="md">
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Дата</Table.Th>
                <Table.Th>Материал</Table.Th>
                <Table.Th>Количество</Table.Th>
                <Table.Th>Цена</Table.Th>
                <Table.Th>Сумма</Table.Th>
                <Table.Th>Остаток после</Table.Th>
                <Table.Th>Причина</Table.Th>
                {canManage ? <Table.Th /> : null}
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {data.actual_material_consumption.map((item) => (
                <Table.Tr key={item.movement_id}>
                  <Table.Td>{formatDateTime(item.movement_date)}</Table.Td>
                  <Table.Td>
                    <Text fw={700}>{item.material_name}</Text>
                    <Text c="dimmed" size="sm">
                      {item.material_category ?? "Без категории"} · {formatMaterialUnit(item.unit)}
                    </Text>
                  </Table.Td>
                  <Table.Td>{formatNumber(item.quantity, 3)}</Table.Td>
                  <Table.Td>{formatCurrency(item.unit_cost)}</Table.Td>
                  <Table.Td>{formatCurrency(item.total_cost)}</Table.Td>
                  <Table.Td>{formatNumber(item.balance_after, 3)}</Table.Td>
                  <Table.Td>{item.reason ?? "—"}</Table.Td>
                  {canManage ? (
                    <Table.Td>
                      <Group gap="xs" justify="flex-end">
                        {onEdit ? (
                          <Tooltip label="Изменить списание">
                            <ActionIcon variant="light" onClick={() => onEdit(item.movement_id)}>
                              <IconPencil size={16} />
                            </ActionIcon>
                          </Tooltip>
                        ) : null}
                        {onDelete ? (
                          <Tooltip label="Удалить списание">
                            <ActionIcon color="red" variant="light" onClick={() => onDelete(item.movement_id)}>
                              <IconTrash size={16} />
                            </ActionIcon>
                          </Tooltip>
                        ) : null}
                      </Group>
                    </Table.Td>
                  ) : null}
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </Table.ScrollContainer>
      ) : (
        <Text c="dimmed">Ручные списания материалов за выбранный период отсутствуют.</Text>
      )}
    </SectionCard>
  );
}

export function NaradMaterialConsumptionReportSection({ data }: { data: ReportsSnapshot }) {
  return (
    <SectionCard padding="xl">
      {data.narad_material_consumption.length ? (
        <Table.ScrollContainer minWidth={1380}>
          <Table highlightOnHover verticalSpacing="md">
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Дата</Table.Th>
                <Table.Th>Наряд</Table.Th>
                <Table.Th>Заказ</Table.Th>
                <Table.Th>Материал</Table.Th>
                <Table.Th>Количество</Table.Th>
                <Table.Th>Цена</Table.Th>
                <Table.Th>Сумма</Table.Th>
                <Table.Th>Остаток после</Table.Th>
                <Table.Th>Причина</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {data.narad_material_consumption.map((item) => (
                <Table.Tr key={item.movement_id}>
                  <Table.Td>{formatDateTime(item.movement_date)}</Table.Td>
                  <Table.Td>
                    <Text fw={700}>{item.narad_number}</Text>
                    <Text c="dimmed" size="sm">
                      {item.client_name}
                    </Text>
                    <Text c="dimmed" size="sm">
                      {item.narad_title}
                    </Text>
                  </Table.Td>
                  <Table.Td>{item.work_order_number}</Table.Td>
                  <Table.Td>
                    <Text fw={700}>{item.material_name}</Text>
                    <Text c="dimmed" size="sm">
                      {item.material_category ?? "Без категории"} · {formatMaterialUnit(item.unit)}
                    </Text>
                  </Table.Td>
                  <Table.Td>{formatNumber(item.quantity, 3)}</Table.Td>
                  <Table.Td>{formatCurrency(item.unit_cost)}</Table.Td>
                  <Table.Td>{formatCurrency(item.total_cost)}</Table.Td>
                  <Table.Td>{formatNumber(item.balance_after, 3)}</Table.Td>
                  <Table.Td>{item.reason ?? "—"}</Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </Table.ScrollContainer>
      ) : (
        <Text c="dimmed">Списания материалов по нарядам за выбранный период отсутствуют.</Text>
      )}
    </SectionCard>
  );
}
