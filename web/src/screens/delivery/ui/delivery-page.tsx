"use client";

import { useDisclosure } from "@mantine/hooks";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import {
  buildDeliveryManifestUrl,
  markDeliverySent
} from "@/entities/delivery/api/delivery-api";
import { useAuthSession } from "@/entities/auth/model/auth-session-context";
import { DeliveryItem } from "@/entities/delivery/model/types";
import { deliveryQueryKeys } from "@/entities/delivery/model/query-keys";
import { naradsQueryKeys } from "@/entities/narads/model/query-keys";
import { worksQueryKeys } from "@/entities/works/model/query-keys";
import { EditDeliveryContactModal } from "@/features/delivery/edit-delivery-contact/ui/edit-delivery-contact-modal";
import { NaradDetailDrawer } from "@/features/narads/view-narad/ui/narad-detail-drawer";
import { hasPermission } from "@/shared/lib/auth/permissions";
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
  const { session } = useAuthSession();
  const [editDeliveryItem, setEditDeliveryItem] = useState<DeliveryItem | null>(null);
  const [editDeliveryOpened, editDeliveryHandlers] = useDisclosure(false);
  const canEditDelivery = hasPermission(session?.user.permission_codes, "clients.manage");

  const markSentMutation = useMutation({
    mutationFn: () => markDeliverySent({ narad_ids: page.selectedNaradIds }),
    onSuccess(result) {
      queryClient.invalidateQueries({ queryKey: deliveryQueryKeys.root });
      queryClient.invalidateQueries({ queryKey: naradsQueryKeys.root });
      queryClient.invalidateQueries({ queryKey: worksQueryKeys.root });
      showSuccessNotification(`Отправка отмечена для ${result.updated_count} наряд(ов).`);
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
          sortBy={page.sortBy}
          sortDirection={page.sortDirection}
          clients={page.clientsQuery.data?.items ?? []}
          executors={page.executorsQuery.data?.items ?? []}
          selectedCount={page.selectedNaradIds.length}
          markSentLoading={markSentMutation.isPending}
          onSearchChange={page.setSearch}
          onClientChange={page.setClientId}
          onExecutorChange={page.setExecutorId}
          onSentFilterChange={page.setSentFilter}
          onSortByChange={page.setSortBy}
          onSortDirectionChange={page.setSortDirection}
          onPrint={() => openPrintDocument(buildDeliveryManifestUrl(page.selectedNaradIds))}
          onMarkSent={() => markSentMutation.mutate()}
        />
        <DeliveryTable
          isLoading={page.deliveryQuery.isLoading}
          items={page.deliveryQuery.data?.items ?? []}
          meta={page.deliveryQuery.data?.meta}
          selectedIds={page.selectedNaradIds}
          onToggleSelected={page.toggleSelected}
          onToggleAll={page.toggleSelectAll}
          onPageChange={page.setPage}
          onView={page.openView}
          canEditDelivery={canEditDelivery}
          onEditDelivery={(item) => {
            setEditDeliveryItem(item);
            editDeliveryHandlers.open();
          }}
        />
      </PageHeading>

      <NaradDetailDrawer
        naradId={page.selectedNaradId}
        opened={page.detailOpened}
        onClose={page.closeDetail}
      />
      <EditDeliveryContactModal
        item={editDeliveryItem}
        opened={editDeliveryOpened}
        onClose={() => {
          setEditDeliveryItem(null);
          editDeliveryHandlers.close();
        }}
      />
    </>
  );
}
