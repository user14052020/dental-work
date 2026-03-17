"use client";

import { ClientDetailDrawer } from "@/features/clients/view-client/ui/client-detail-drawer";
import { ClientFormModal } from "@/features/clients/upsert-client/ui/client-form-modal";
import { openAfterDrawerClose } from "@/shared/lib/ui/open-after-drawer-close";
import { PageHeading } from "@/shared/ui/page-heading";
import { ClientsToolbar } from "@/widgets/clients-panel/ui/clients-toolbar";
import { ClientsTable } from "@/widgets/clients-panel/ui/clients-table";

import { useClientsPage } from "../model/use-clients-page";

export function ClientsPage() {
  const page = useClientsPage();

  return (
    <>
      <PageHeading
        title="Клиенты"
        description="Поисковый и финансовый реестр по клиникам: контакты, объем заказов, задолженность и история работ."
      >
        <ClientsToolbar search={page.search} onCreate={page.openCreate} onSearchChange={page.setSearch} />
        <ClientsTable
          isLoading={page.clientsQuery.isLoading}
          items={page.clientsQuery.data?.items ?? []}
          meta={page.clientsQuery.data?.meta}
          onEdit={page.openEdit}
          onPageChange={page.setPage}
          onView={page.openView}
        />
      </PageHeading>

      <ClientFormModal client={page.editedClient} opened={page.formOpened} onClose={page.closeForm} />

      <ClientDetailDrawer
        clientId={page.selectedClient?.id}
        opened={page.detailOpened}
        onClose={page.closeDetail}
        onEdit={() => {
          const client = page.selectedClient;
          if (client) {
            page.closeDetail();
            openAfterDrawerClose(() => page.openEdit(client));
          }
        }}
      />
    </>
  );
}
