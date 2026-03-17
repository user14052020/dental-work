"use client";

import { WorkCatalogItemFormModal } from "@/features/work-catalog/upsert-work-catalog-item/ui/work-catalog-item-form-modal";
import { PageHeading } from "@/shared/ui/page-heading";
import { WorkCatalogTable } from "@/widgets/work-catalog-panel/ui/work-catalog-table";
import { WorkCatalogToolbar } from "@/widgets/work-catalog-panel/ui/work-catalog-toolbar";

import { useWorkCatalogPage } from "../model/use-work-catalog-page";

export function WorkCatalogPage() {
  const page = useWorkCatalogPage();

  return (
    <>
      <PageHeading
        title="Каталог работ"
        description="Шаблоны лабораторных работ с базовой ценой и набором производственных операций. Этот слой готовит переход к полноценным нарядам."
      >
        <WorkCatalogToolbar
          activeOnly={page.activeOnly}
          onActiveOnlyChange={page.setActiveOnly}
          onCreate={page.openCreate}
          onSearchChange={page.setSearch}
          search={page.search}
        />
        <WorkCatalogTable
          isLoading={page.workCatalogQuery.isLoading}
          items={page.workCatalogQuery.data?.items ?? []}
          meta={page.workCatalogQuery.data?.meta}
          onEdit={page.openEdit}
          onPageChange={page.setPage}
        />
      </PageHeading>

      <WorkCatalogItemFormModal
        item={page.editedItem}
        opened={page.formOpened}
        onClose={page.closeForm}
      />
    </>
  );
}
