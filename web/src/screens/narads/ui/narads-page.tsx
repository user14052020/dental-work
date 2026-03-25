"use client";

import { NaradLifecycleModal } from "@/features/narads/manage-lifecycle/ui/narad-lifecycle-modal";
import { NaradFormModal } from "@/features/narads/upsert-narad/ui/narad-form-modal";
import { NaradDetailDrawer } from "@/features/narads/view-narad/ui/narad-detail-drawer";
import { WorkFormModal } from "@/features/works/create-work/ui/work-form-modal";
import { openAfterDrawerClose } from "@/shared/lib/ui/open-after-drawer-close";
import { PageHeading } from "@/shared/ui/page-heading";
import { NaradsTable } from "@/widgets/narads-panel/ui/narads-table";
import { NaradsToolbar } from "@/widgets/narads-panel/ui/narads-toolbar";

import { useNaradsPage } from "../model/use-narads-page";

export function NaradsPage() {
  const page = useNaradsPage();

  return (
    <>
      <PageHeading
        title="Наряды"
        description="Шапки заказов как отдельный реестр. Этот слой отделяет производственную карточку заказа от внутренних строк работ и готовит переход к полноценной модели лабораторного наряда."
      >
        <NaradsToolbar
          clientId={page.clientId}
          clients={page.clientsQuery.data?.items ?? []}
          dateFrom={page.dateFrom}
          dateTo={page.dateTo}
          onClientChange={page.setClientId}
          onDateFromChange={page.setDateFrom}
          onDateToChange={page.setDateTo}
          onCreate={page.openCreateNarad}
          onSearchChange={page.setSearch}
          onStatusChange={page.setStatus}
          search={page.search}
          status={page.status}
        />
        <NaradsTable
          isLoading={page.naradsQuery.isLoading}
          items={page.naradsQuery.data?.items ?? []}
          meta={page.naradsQuery.data?.meta}
          onPageChange={page.setPage}
          onView={page.openView}
        />
      </PageHeading>

      <NaradFormModal narad={page.editingNarad} opened={page.naradFormOpened} onClose={page.closeNaradForm} />
      <WorkFormModal initialNarad={page.workNarad} opened={page.workFormOpened} onClose={page.closeCreateWork} />
      <NaradLifecycleModal
        mode={page.lifecycleMode}
        narad={page.lifecycleNarad}
        opened={page.lifecycleOpened}
        onClose={page.closeLifecycle}
      />
      <NaradDetailDrawer
        naradId={page.selectedNarad?.id}
        opened={page.detailOpened}
        onClose={page.closeDetail}
        onEdit={(narad) => {
          page.closeDetail();
          openAfterDrawerClose(() => page.openEditNarad(narad));
        }}
        onAddWork={(narad) => {
          page.closeDetail();
          openAfterDrawerClose(() => page.openCreateWork(narad));
        }}
        onCloseNarad={(narad) => {
          page.closeDetail();
          openAfterDrawerClose(() => page.openCloseLifecycle(narad));
        }}
        onReopenNarad={(narad) => {
          page.closeDetail();
          openAfterDrawerClose(() => page.openReopenLifecycle(narad));
        }}
      />
    </>
  );
}
