"use client";

import { useDebouncedValue, useDisclosure } from "@mantine/hooks";
import { useEffect, useState } from "react";

import { Executor } from "@/entities/executors/model/types";
import { useExecutorsQuery } from "@/entities/executors/model/use-executors-query";

export function useExecutorsPage() {
  const [search, setSearch] = useState("");
  const [activeOnly, setActiveOnly] = useState(false);
  const [page, setPage] = useState(1);
  const [selectedExecutor, setSelectedExecutor] = useState<Executor | null>(null);
  const [editedExecutor, setEditedExecutor] = useState<Executor | null>(null);
  const [debouncedSearch] = useDebouncedValue(search, 300);
  const [detailOpened, detailHandlers] = useDisclosure(false);
  const [formOpened, formHandlers] = useDisclosure(false);

  useEffect(() => {
    setPage(1);
  }, [activeOnly, debouncedSearch]);

  const executorsQuery = useExecutorsQuery({
    page,
    page_size: 10,
    search: debouncedSearch || undefined,
    active_only: activeOnly || undefined
  });

  return {
    activeOnly,
    detailOpened,
    editedExecutor,
    executorsQuery,
    formOpened,
    page,
    search,
    selectedExecutor,
    setActiveOnly,
    setPage,
    setSearch,
    openCreate() {
      setEditedExecutor(null);
      formHandlers.open();
    },
    openEdit(executor: Executor) {
      setEditedExecutor(executor);
      formHandlers.open();
    },
    openView(executor: Executor) {
      setSelectedExecutor(executor);
      detailHandlers.open();
    },
    closeForm() {
      setEditedExecutor(null);
      formHandlers.close();
    },
    closeDetail() {
      setSelectedExecutor(null);
      detailHandlers.close();
    }
  };
}
