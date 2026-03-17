"use client";

import { Button, Group, Stack, Text } from "@mantine/core";
import { IconPlus } from "@tabler/icons-react";

import { ExecutorCategoryFormModal } from "@/features/operations/upsert-category/ui/executor-category-form-modal";
import { OperationFormModal } from "@/features/operations/upsert-operation/ui/operation-form-modal";
import { PageHeading } from "@/shared/ui/page-heading";
import { ExecutorCategoriesTable } from "@/widgets/operations-panel/ui/executor-categories-table";
import { OperationsTable } from "@/widgets/operations-panel/ui/operations-table";
import { OperationsToolbar } from "@/widgets/operations-panel/ui/operations-toolbar";

import { useOperationsPage } from "../model/use-operations-page";

export function OperationsPage() {
  const page = useOperationsPage();
  const categories = page.categoriesQuery.data?.items ?? [];

  return (
    <>
      <PageHeading
        title="Операции"
        description="Каталог лабораторных операций, тарифы по категориям оплаты и подготовка типовых производственных шагов для заказов."
      >
        <Stack gap="md">
          <Group justify="space-between" align="center">
            <div>
              <Text fw={700} size="lg">
                Категории оплаты техников
              </Text>
              <Text c="dimmed" size="sm">
                Эти категории назначаются исполнителям и используются в ставках операций.
              </Text>
            </div>
            <Button
              leftSection={<IconPlus size={16} />}
              onClick={page.openCreateCategory}
              className="w-full md:w-auto"
            >
              Новая категория
            </Button>
          </Group>
          <ExecutorCategoriesTable
            isLoading={page.categoriesQuery.isLoading}
            items={categories}
            onEdit={page.openEditCategory}
          />
        </Stack>

        <OperationsToolbar
          activeOnly={page.activeOnly}
          onActiveOnlyChange={page.setActiveOnly}
          onCreate={page.openCreateOperation}
          onSearchChange={page.setSearch}
          search={page.search}
        />
        <OperationsTable
          isLoading={page.operationsQuery.isLoading}
          items={page.operationsQuery.data?.items ?? []}
          meta={page.operationsQuery.data?.meta}
          onEdit={page.openEditOperation}
          onPageChange={page.setPage}
        />
      </PageHeading>

      <ExecutorCategoryFormModal
        category={page.editedCategory}
        opened={page.categoryFormOpened}
        onClose={page.closeCategoryForm}
      />
      <OperationFormModal
        categories={categories}
        operation={page.editedOperation}
        opened={page.operationFormOpened}
        onClose={page.closeOperationForm}
      />
    </>
  );
}
