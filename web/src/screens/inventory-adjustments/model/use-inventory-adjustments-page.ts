"use client";

import { useDebouncedValue, useDisclosure } from "@mantine/hooks";
import { useEffect, useState } from "react";

import { InventoryAdjustmentCompact } from "@/entities/inventory-adjustments/model/types";
import { useInventoryAdjustmentsQuery } from "@/entities/inventory-adjustments/model/use-inventory-adjustments-query";

function toIsoDate(value: string) {
  return value ? new Date(value).toISOString() : undefined;
}

export function useInventoryAdjustmentsPage() {
  const [search, setSearch] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [page, setPage] = useState(1);
  const [selectedAdjustment, setSelectedAdjustment] = useState<InventoryAdjustmentCompact | null>(null);
  const [debouncedSearch] = useDebouncedValue(search, 300);
  const [detailOpened, detailHandlers] = useDisclosure(false);
  const [formOpened, formHandlers] = useDisclosure(false);

  useEffect(() => {
    setPage(1);
  }, [debouncedSearch, dateFrom, dateTo]);

  const adjustmentsQuery = useInventoryAdjustmentsQuery({
    page,
    page_size: 10,
    search: debouncedSearch || undefined,
    date_from: toIsoDate(dateFrom),
    date_to: toIsoDate(dateTo)
  });

  return {
    adjustmentsQuery,
    dateFrom,
    dateTo,
    detailOpened,
    formOpened,
    page,
    search,
    selectedAdjustment,
    setDateFrom,
    setDateTo,
    setPage,
    setSearch,
    openCreate() {
      formHandlers.open();
    },
    closeCreate() {
      formHandlers.close();
    },
    openView(adjustment: InventoryAdjustmentCompact) {
      setSelectedAdjustment(adjustment);
      detailHandlers.open();
    },
    closeDetail() {
      setSelectedAdjustment(null);
      detailHandlers.close();
    }
  };
}
