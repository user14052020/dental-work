"use client";

import { NaradDetailDrawer } from "@/features/narads/view-narad/ui/narad-detail-drawer";
import { OutsideWorkStatusModal } from "@/features/outside-works/manage-outside-work/ui/outside-work-status-modal";
import { PageHeading } from "@/shared/ui/page-heading";
import { OutsideWorksTable } from "@/widgets/outside-works-panel/ui/outside-works-table";
import { OutsideWorksToolbar } from "@/widgets/outside-works-panel/ui/outside-works-toolbar";

import { useOutsideWorksPage } from "../model/use-outside-works-page";

export function OutsideWorksPage() {
  const page = useOutsideWorksPage();

  return (
    <>
      <PageHeading
        title="Работы на стороне"
        description="Наряды, переданные подрядчикам: внешний номер, сроки возврата и стоимость внешнего производства."
      >
        <OutsideWorksToolbar
          search={page.search}
          clientId={page.clientId}
          state={page.state}
          clients={page.clientsQuery.data?.items ?? []}
          onSearchChange={page.setSearch}
          onClientChange={page.setClientId}
          onStateChange={page.setState}
        />
        <OutsideWorksTable
          items={page.outsideWorksQuery.data?.items ?? []}
          meta={page.outsideWorksQuery.data?.meta}
          isLoading={page.outsideWorksQuery.isLoading}
          onPageChange={page.setPage}
          onView={page.openView}
          onMarkSent={page.openMarkSent}
          onMarkReturned={page.openMarkReturned}
        />
      </PageHeading>

      <NaradDetailDrawer naradId={page.selectedNaradId} opened={page.detailOpened} onClose={page.closeDetail} />
      <OutsideWorkStatusModal item={page.selectedItem} mode={page.mode} opened={page.modalOpened} onClose={page.closeModal} />
    </>
  );
}
