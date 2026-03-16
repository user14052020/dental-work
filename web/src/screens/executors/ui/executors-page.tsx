"use client";

import { ExecutorDetailDrawer } from "@/features/executors/view-executor/ui/executor-detail-drawer";
import { ExecutorFormModal } from "@/features/executors/upsert-executor/ui/executor-form-modal";
import { PageHeading } from "@/shared/ui/page-heading";
import { ExecutorsTable } from "@/widgets/executors-panel/ui/executors-table";
import { ExecutorsToolbar } from "@/widgets/executors-panel/ui/executors-toolbar";

import { useExecutorsPage } from "../model/use-executors-page";

export function ExecutorsPage() {
  const page = useExecutorsPage();

  return (
    <>
      <PageHeading
        title="Исполнители"
        description="Каталог исполнителей с поиском по реквизитам, фильтром активности, ставками и производственной нагрузкой."
      >
        <ExecutorsToolbar
          activeOnly={page.activeOnly}
          onActiveOnlyChange={page.setActiveOnly}
          onCreate={page.openCreate}
          onSearchChange={page.setSearch}
          search={page.search}
        />
        <ExecutorsTable
          isLoading={page.executorsQuery.isLoading}
          items={page.executorsQuery.data?.items ?? []}
          meta={page.executorsQuery.data?.meta}
          onEdit={page.openEdit}
          onPageChange={page.setPage}
          onView={page.openView}
        />
      </PageHeading>

      <ExecutorFormModal executor={page.editedExecutor} opened={page.formOpened} onClose={page.closeForm} />

      <ExecutorDetailDrawer
        executorId={page.selectedExecutor?.id}
        opened={page.detailOpened}
        onClose={page.closeDetail}
        onEdit={() => {
          if (page.selectedExecutor) {
            page.openEdit(page.selectedExecutor);
          }
        }}
      />
    </>
  );
}
