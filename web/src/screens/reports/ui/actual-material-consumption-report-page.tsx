"use client";

import { useDisclosure } from "@mantine/hooks";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import {
  deleteManualMaterialConsumption,
  updateManualMaterialConsumption
} from "@/entities/materials/api/materials-api";
import { materialsQueryKeys } from "@/entities/materials/model/query-keys";
import { reportsQueryKeys } from "@/entities/reports/model/query-keys";
import { ActualMaterialConsumptionReportItem, ReportsSnapshot } from "@/entities/reports/model/types";
import { EditActualConsumptionModal } from "@/features/materials/edit-actual-consumption/ui/edit-actual-consumption-modal";
import { ActualMaterialConsumptionReportSection } from "@/screens/reports/ui/report-sections";
import { ReportsPageShell } from "@/screens/reports/ui/reports-shell";
import { showErrorNotification } from "@/shared/lib/notifications/show-error";
import { showSuccessNotification } from "@/shared/lib/notifications/show-success";

function ActualMaterialConsumptionReportContent({ data }: { data: ReportsSnapshot }) {
  const queryClient = useQueryClient();
  const [editedEntry, setEditedEntry] = useState<ActualMaterialConsumptionReportItem | null>(null);
  const [editOpened, editHandlers] = useDisclosure(false);

  const updateMutation = useMutation({
    mutationFn: async (payload: { quantity: string; reason?: string }) => {
      if (!editedEntry) {
        throw new Error("Строка списания не выбрана.");
      }

      return updateManualMaterialConsumption(editedEntry.movement_id, payload);
    },
    onSuccess() {
      queryClient.invalidateQueries({ queryKey: reportsQueryKeys.root });
      queryClient.invalidateQueries({ queryKey: materialsQueryKeys.root });
      showSuccessNotification("Списание по факту обновлено.");
      editHandlers.close();
      setEditedEntry(null);
    },
    onError(error) {
      showErrorNotification(error, "Не удалось обновить списание.");
    }
  });

  const deleteMutation = useMutation({
    mutationFn: (movementId: string) => deleteManualMaterialConsumption(movementId),
    onSuccess() {
      queryClient.invalidateQueries({ queryKey: reportsQueryKeys.root });
      queryClient.invalidateQueries({ queryKey: materialsQueryKeys.root });
      showSuccessNotification("Списание по факту удалено.");
    },
    onError(error) {
      showErrorNotification(error, "Не удалось удалить списание.");
    }
  });

  return (
    <>
      <ActualMaterialConsumptionReportSection
        data={data}
        onEdit={(movementId) => {
          const entry = data.actual_material_consumption.find((item) => item.movement_id === movementId);
          if (!entry) {
            return;
          }
          setEditedEntry(entry);
          editHandlers.open();
        }}
        onDelete={(movementId) => {
          const entry = data.actual_material_consumption.find((item) => item.movement_id === movementId);
          if (!entry) {
            return;
          }
          if (!window.confirm(`Удалить списание ${entry.material_name} на ${entry.quantity}?`)) {
            return;
          }
          deleteMutation.mutate(movementId);
        }}
      />
      <EditActualConsumptionModal
        entry={editedEntry}
        opened={editOpened}
        loading={updateMutation.isPending}
        onClose={() => {
          setEditedEntry(null);
          editHandlers.close();
        }}
        onSubmit={(payload) => updateMutation.mutate(payload)}
      />
    </>
  );
}

export function ActualMaterialConsumptionReportPage() {
  return (
    <ReportsPageShell
      title="Расход по факту"
      description="Отдельный отчет по ручным списаниям материалов без привязки к заказу."
      content={(data) => <ActualMaterialConsumptionReportContent data={data} />}
    />
  );
}
