"use client";

import { useDebouncedValue, useDisclosure } from "@mantine/hooks";
import { useEffect, useState } from "react";

import { MaterialReceiptCompact } from "@/entities/receipts/model/types";
import { useReceiptsQuery } from "@/entities/receipts/model/use-receipts-query";

function toIsoDate(value: string) {
  return value ? new Date(value).toISOString() : undefined;
}

export function useReceiptsPage() {
  const [search, setSearch] = useState("");
  const [supplier, setSupplier] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [page, setPage] = useState(1);
  const [selectedReceipt, setSelectedReceipt] = useState<MaterialReceiptCompact | null>(null);
  const [debouncedSearch] = useDebouncedValue(search, 300);
  const [detailOpened, detailHandlers] = useDisclosure(false);
  const [formOpened, formHandlers] = useDisclosure(false);

  useEffect(() => {
    setPage(1);
  }, [debouncedSearch, supplier, dateFrom, dateTo]);

  const receiptsQuery = useReceiptsQuery({
    page,
    page_size: 10,
    search: debouncedSearch || undefined,
    supplier: supplier || undefined,
    date_from: toIsoDate(dateFrom),
    date_to: toIsoDate(dateTo)
  });

  return {
    dateFrom,
    dateTo,
    detailOpened,
    formOpened,
    page,
    receiptsQuery,
    search,
    selectedReceipt,
    setDateFrom,
    setDateTo,
    setPage,
    setSearch,
    setSupplier,
    supplier,
    openCreate() {
      formHandlers.open();
    },
    closeCreate() {
      formHandlers.close();
    },
    openView(receipt: MaterialReceiptCompact) {
      setSelectedReceipt(receipt);
      detailHandlers.open();
    },
    closeDetail() {
      setSelectedReceipt(null);
      detailHandlers.close();
    }
  };
}
