"use client";

import { useDebouncedValue, useDisclosure } from "@mantine/hooks";
import { useEffect, useState } from "react";

import { WorkCatalogItem } from "@/entities/work-catalog/model/types";
import { useWorkCatalogQuery } from "@/entities/work-catalog/model/use-work-catalog-query";

export function useWorkCatalogPage() {
  const [search, setSearch] = useState("");
  const [activeOnly, setActiveOnly] = useState(false);
  const [page, setPage] = useState(1);
  const [editedItem, setEditedItem] = useState<WorkCatalogItem | null>(null);
  const [debouncedSearch] = useDebouncedValue(search, 300);
  const [formOpened, formHandlers] = useDisclosure(false);

  useEffect(() => {
    setPage(1);
  }, [activeOnly, debouncedSearch]);

  const workCatalogQuery = useWorkCatalogQuery({
    page,
    page_size: 10,
    search: debouncedSearch || undefined,
    active_only: activeOnly || undefined
  });

  return {
    activeOnly,
    editedItem,
    formOpened,
    page,
    search,
    setActiveOnly,
    setPage,
    setSearch,
    workCatalogQuery,
    openCreate() {
      setEditedItem(null);
      formHandlers.open();
    },
    openEdit(item: WorkCatalogItem) {
      setEditedItem(item);
      formHandlers.open();
    },
    closeForm() {
      setEditedItem(null);
      formHandlers.close();
    }
  };
}
