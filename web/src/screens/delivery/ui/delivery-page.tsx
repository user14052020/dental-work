"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import {
  buildDeliveryManifestUrl,
  markDeliverySent
} from "@/entities/delivery/api/delivery-api";
import { deliveryQueryKeys } from "@/entities/delivery/model/query-keys";
import { worksQueryKeys } from "@/entities/works/model/query-keys";
import { WorkDetailDrawer } from "@/features/works/view-work/ui/work-detail-drawer";
import { showErrorNotification } from "@/shared/lib/notifications/show-error";
import { showSuccessNotification } from "@/shared/lib/notifications/show-success";
import { PageHeading } from "@/shared/ui/page-heading";
import { DeliveryTable } from "@/widgets/delivery-panel/ui/delivery-table";
import { DeliveryToolbar } from "@/widgets/delivery-panel/ui/delivery-toolbar";

import { useDeliveryPage } from "../model/use-delivery-page";

function openPrintDocument(path: string) {
  if (typeof window === "undefined") {
    return;
  }

  window.open(path, "_blank", "noopener,noreferrer");
}

export function DeliveryPage() {
  const page = useDeliveryPage();
  const queryClient = useQueryClient();

  const markSentMutation = useMutation({
    mutationFn: () => markDeliverySent({ work_ids: page.selectedWorkIds }),
    onSuccess(result) {
      queryClient.invalidateQueries({ queryKey: deliveryQueryKeys.root });
      queryClient.invalidateQueries({ queryKey: worksQueryKeys.root });
      showSuccessNotification(`Отправка отмечена для ${result.updated_count} заказ(ов).`);
      page.clearSelection();
    },
    onError(error) {
      showErrorNotification(error, "Не удалось отметить отправку.");
    }
  });

  return (
    <>
      <PageHeading
        title="Доставка"
        description="Реестр готовых заказов к отправке: адрес, контакт, печатный лист для курьера и фиксация факта отправки."
      >
        <DeliveryToolbar
          search={page.search}
          clientId={page.clientId}
          executorId={page.executorId}
          sentFilter={page.sentFilter}
          clients={page.clientsQuery.data?.items ?? []}
          executors={page.executorsQuery.data?.items ?? []}
          selectedCount={page.selectedWorkIds.length}
          markSentLoading={markSentMutation.isPending}
          onSearchChange={page.setSearch}
          onClientChange={page.setClientId}
          onExecutorChange={page.setExecutorId}
          onSentFilterChange={page.setSentFilter}
          onPrint={() => openPrintDocument(buildDeliveryManifestUrl(page.selectedWorkIds))}
          onMarkSent={() => markSentMutation.mutate()}
        />
        <DeliveryTable
          isLoading={page.deliveryQuery.isLoading}
          items={page.deliveryQuery.data?.items ?? []}
          meta={page.deliveryQuery.data?.meta}
          selectedIds={page.selectedWorkIds}
          onToggleSelected={page.toggleSelected}
          onToggleAll={page.toggleSelectAll}
          onPageChange={page.setPage}
          onView={page.openView}
        />
      </PageHeading>

      <WorkDetailDrawer
        workId={page.selectedWorkId}
        opened={page.detailOpened}
        onClose={page.closeDetail}
      />
    </>
  );
}
