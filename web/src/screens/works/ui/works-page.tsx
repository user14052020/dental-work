"use client";

import { WorkFormModal } from "@/features/works/create-work/ui/work-form-modal";
import { WorkStatusModal } from "@/features/works/update-work-status/ui/work-status-modal";
import { WorkDetailDrawer } from "@/features/works/view-work/ui/work-detail-drawer";
import { PageHeading } from "@/shared/ui/page-heading";
import { WorksTable } from "@/widgets/works-panel/ui/works-table";
import { WorksToolbar } from "@/widgets/works-panel/ui/works-toolbar";

import { useWorksPage } from "../model/use-works-page";

export function WorksPage() {
  const page = useWorksPage();

  return (
    <>
      <PageHeading
        title="Работы"
        description="Реестр заказов с полнотекстовым поиском, фильтрами по статусам и связями с клиентами, исполнителями и материалами."
      >
        <WorksToolbar
          clientId={page.clientId}
          clients={page.clientsQuery.data?.items ?? []}
          dateFrom={page.dateFrom}
          dateTo={page.dateTo}
          executorId={page.executorId}
          executors={page.executorsQuery.data?.items ?? []}
          onClientChange={page.setClientId}
          onCreate={page.openCreate}
          onDateFromChange={page.setDateFrom}
          onDateToChange={page.setDateTo}
          onExecutorChange={page.setExecutorId}
          onSearchChange={page.setSearch}
          onStatusChange={page.setStatus}
          search={page.search}
          status={page.status}
        />
        <WorksTable
          isLoading={page.worksQuery.isLoading}
          items={page.worksQuery.data?.items ?? []}
          meta={page.worksQuery.data?.meta}
          onPageChange={page.setPage}
          onStatusChange={page.openStatus}
          onView={page.openView}
        />
      </PageHeading>

      <WorkFormModal opened={page.formOpened} onClose={page.closeCreate} />
      <WorkStatusModal opened={page.statusOpened} onClose={page.closeStatus} work={page.statusWork} />
      <WorkDetailDrawer
        onClose={page.closeDetail}
        onStatusChange={() => {
          if (page.selectedWork) {
            page.openStatus(page.selectedWork);
          }
        }}
        opened={page.detailOpened}
        workId={page.selectedWork?.id}
      />
    </>
  );
}
