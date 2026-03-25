"use client";

import { Stack, Text } from "@mantine/core";
import Link from "next/link";

import { reportDefinitions } from "@/screens/reports/ui/report-definitions";
import { PageHeading } from "@/shared/ui/page-heading";
import { SectionCard } from "@/shared/ui/section-card";

export function ReportsPage() {
  return (
    <PageHeading
      title="Отчеты"
      description="Каталог аналитических отчетов лаборатории. Выбери нужный срез и открой его на отдельной странице."
    >
      <Stack gap="lg">
        <div>
          <Text c="dimmed" size="sm" mt={4}>
            Каждый аналитический блок вынесен на отдельную страницу с собственным URL и общим фильтром периода.
          </Text>
        </div>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-3">
          {reportDefinitions
            .filter((item) => item.href !== "/reports")
            .map((item) => (
              <Link key={item.href} href={item.href} className="no-underline">
                <SectionCard padding="xl">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <Text fw={700} size="lg">
                        {item.title}
                      </Text>
                      <Text c="dimmed" size="sm" mt={6}>
                        {item.description}
                      </Text>
                    </div>
                    <item.icon size={24} />
                  </div>
                </SectionCard>
              </Link>
            ))}
        </div>
      </Stack>
    </PageHeading>
  );
}
