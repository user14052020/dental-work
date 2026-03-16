import { Alert, Group, Loader, List, SimpleGrid, Stack, Text, ThemeIcon } from "@mantine/core";
import {
  IconAlertTriangle,
  IconChartBar,
  IconClockHour4,
  IconCoin,
  IconFlask2,
  IconReceipt2,
  IconUsers
} from "@tabler/icons-react";
import { ReactNode } from "react";

import { DashboardSnapshot } from "@/entities/dashboard/model/types";
import { formatCurrency } from "@/shared/lib/formatters/format-currency";
import { formatDateTime } from "@/shared/lib/formatters/format-date";
import { KpiCard } from "@/shared/ui/kpi-card";
import { SectionCard } from "@/shared/ui/section-card";

type DashboardOverviewProps = {
  data?: DashboardSnapshot;
  isLoading: boolean;
  isError: boolean;
};

type DashboardInsetCardProps = {
  title: string;
  description: string;
  value?: string;
  icon: ReactNode;
  compactValue?: boolean;
};

function DashboardInsetCard({ title, description, value, icon, compactValue = false }: DashboardInsetCardProps) {
  return (
    <div className="h-full rounded-[24px] border border-white/60 bg-white/72 p-5">
      <Stack gap="md" className="h-full">
        <ThemeIcon size={44} radius="xl" color="teal" variant="light">
          {icon}
        </ThemeIcon>
        <Stack gap={6} className="mt-auto">
          <Text c="dimmed" size="sm">
            {title}
          </Text>
          {value ? (
            <Text
              fw={800}
              component="div"
              className={compactValue ? "text-[1.1rem] leading-tight md:text-[1.35rem]" : "text-[1.9rem] leading-none"}
            >
              {value}
            </Text>
          ) : null}
          <Text c="dimmed" size="sm">
            {description}
          </Text>
        </Stack>
      </Stack>
    </div>
  );
}

function DashboardTopList({
  title,
  items,
  emptyMessage
}: {
  title: string;
  items: { id: string; label: string; work_count: number; amount: string }[];
  emptyMessage: string;
}) {
  return (
    <SectionCard className="h-full" padding="xl">
      <Stack gap="md">
        <Text fw={700} size="lg">
          {title}
        </Text>
        {items.length ? (
          <List spacing="sm" withPadding>
            {items.map((item) => (
              <List.Item key={item.id}>
                <Group justify="space-between" align="start" wrap="wrap" className="gap-y-1">
                  <Text fw={600}>{item.label}</Text>
                  <Text c="dimmed" size="sm">
                    {item.work_count} работ · {formatCurrency(item.amount)}
                  </Text>
                </Group>
              </List.Item>
            ))}
          </List>
        ) : (
          <Text c="dimmed">{emptyMessage}</Text>
        )}
      </Stack>
    </SectionCard>
  );
}

export function DashboardOverview({ data, isLoading, isError }: DashboardOverviewProps) {
  if (isLoading) {
    return (
      <SectionCard>
        <Group justify="center" py="xl">
          <Loader />
        </Group>
      </SectionCard>
    );
  }

  if (isError || !data) {
    return (
      <Alert color="red" title="Сводка недоступна">
        Не удалось загрузить сводные показатели.
      </Alert>
    );
  }

  return (
    <Stack gap="lg">
      <SimpleGrid cols={{ base: 1, sm: 2, xl: 4 }} spacing="lg" verticalSpacing="lg">
          <KpiCard
            title="Активные работы"
            value={String(data.active_works)}
            hint="Заказы в производственном цикле"
            icon={<IconChartBar size={26} />}
          />
          <KpiCard
            title="Просроченные"
            value={String(data.overdue_works)}
            hint="Требуют приоритизации"
            icon={<IconAlertTriangle size={26} />}
          />
          <KpiCard
            title="Выручка"
            value={formatCurrency(data.revenue)}
            hint="Сумма заказов за период"
            icon={<IconReceipt2 size={26} />}
          />
          <KpiCard
            title="Прибыль"
            value={formatCurrency(data.profit)}
            hint="После вычета материалов и труда"
            icon={<IconCoin size={26} />}
          />
      </SimpleGrid>

      <SimpleGrid cols={{ base: 1, xl: 2 }} spacing="lg" verticalSpacing="lg">
          <SectionCard className="h-full" padding="xl">
            <Stack gap="md">
              <Text fw={700} size="lg">
                Финансовый срез
              </Text>
              <SimpleGrid cols={{ base: 1, sm: 2 }} spacing="md" verticalSpacing="md">
                <DashboardInsetCard
                  title="Материальные расходы"
                  value={formatCurrency(data.material_expenses)}
                  description="Актуальный расход материалов за выбранный период."
                  icon={<IconFlask2 size={20} />}
                />
                <DashboardInsetCard
                  title="Сгенерировано"
                  value={formatDateTime(data.generated_at)}
                  description="Время последнего обновления аналитического среза."
                  compactValue
                  icon={<IconClockHour4 size={20} />}
                />
              </SimpleGrid>
            </Stack>
          </SectionCard>
          <SectionCard className="h-full" padding="xl">
            <Stack gap="md">
              <Text fw={700} size="lg">
                Быстрый обзор
              </Text>
              <SimpleGrid cols={{ base: 1, sm: 2 }} spacing="md" verticalSpacing="md">
                <DashboardInsetCard
                  title="Клиенты"
                  description="Топ по объему заказов и повторным работам вынесен в отдельный блок ниже."
                  icon={<IconUsers size={20} />}
                />
                <DashboardInsetCard
                  title="Материалы"
                  description="Контроль расхода и низких остатков доступен в отдельном рабочем разделе."
                  icon={<IconFlask2 size={20} />}
                />
              </SimpleGrid>
            </Stack>
          </SectionCard>
      </SimpleGrid>

      <SimpleGrid cols={{ base: 1, xl: 2 }} spacing="lg" verticalSpacing="lg">
          <DashboardTopList
            title="Топ клиентов"
            emptyMessage="Пока нет данных по клиентам."
            items={data.top_clients.map((item) => ({
              id: item.id,
              label: item.name ?? "Без названия",
              work_count: item.work_count,
              amount: item.amount
            }))}
          />
          <DashboardTopList
            title="Топ исполнителей"
            emptyMessage="Пока нет данных по исполнителям."
            items={data.top_executors.map((item) => ({
              id: item.id,
              label: item.full_name ?? "Без имени",
              work_count: item.work_count,
              amount: item.amount
            }))}
          />
      </SimpleGrid>
    </Stack>
  );
}
