"use client";

import { ConsumeMaterialModal } from "@/features/materials/consume-material/ui/consume-material-modal";
import { MaterialDetailDrawer } from "@/features/materials/view-material/ui/material-detail-drawer";
import { MaterialFormModal } from "@/features/materials/upsert-material/ui/material-form-modal";
import { PageHeading } from "@/shared/ui/page-heading";
import { MaterialsTable } from "@/widgets/materials-panel/ui/materials-table";
import { MaterialsToolbar } from "@/widgets/materials-panel/ui/materials-toolbar";

import { useMaterialsPage } from "../model/use-materials-page";

export function MaterialsPage() {
  const page = useMaterialsPage();

  return (
    <>
      <PageHeading
        title="Материалы"
        description="Складской учет, низкие остатки, списания и поиск по полному набору реквизитов материала."
      >
        <MaterialsToolbar
          lowStockOnly={page.lowStockOnly}
          onCreate={page.openCreate}
          onLowStockChange={page.setLowStockOnly}
          onSearchChange={page.setSearch}
          search={page.search}
        />
        <MaterialsTable
          isLoading={page.materialsQuery.isLoading}
          items={page.materialsQuery.data?.items ?? []}
          meta={page.materialsQuery.data?.meta}
          onConsume={page.openConsume}
          onEdit={page.openEdit}
          onPageChange={page.setPage}
          onView={page.openView}
        />
      </PageHeading>

      <MaterialFormModal material={page.editedMaterial} opened={page.formOpened} onClose={page.closeForm} />
      <ConsumeMaterialModal materialId={page.consumedMaterial?.id} opened={page.consumeOpened} onClose={page.closeConsume} />
      <MaterialDetailDrawer
        materialId={page.selectedMaterial?.id}
        opened={page.detailOpened}
        onClose={page.closeDetail}
        onConsume={() => {
          if (page.selectedMaterial) {
            page.openConsume(page.selectedMaterial);
          }
        }}
        onEdit={() => {
          if (page.selectedMaterial) {
            page.openEdit(page.selectedMaterial);
          }
        }}
      />
    </>
  );
}
