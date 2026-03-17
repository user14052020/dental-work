"use client";

import { useDebouncedValue, useDisclosure } from "@mantine/hooks";
import { useEffect, useState } from "react";

import { useClientsQuery } from "@/entities/clients/model/use-clients-query";
import { useDeliveryQuery } from "@/entities/delivery/model/use-delivery-query";
import { useExecutorsQuery } from "@/entities/executors/model/use-executors-query";

export function useDeliveryPage() {
  const [search, setSearch] = useState("");
  const [clientId, setClientId] = useState("");
  const [executorId, setExecutorId] = useState("");
  const [sentFilter, setSentFilter] = useState("pending");
  const [page, setPage] = useState(1);
  const [selectedWorkIds, setSelectedWorkIds] = useState<string[]>([]);
  const [selectedWorkId, setSelectedWorkId] = useState<string>();
  const [debouncedSearch] = useDebouncedValue(search, 300);
  const [detailOpened, detailHandlers] = useDisclosure(false);

  useEffect(() => {
    setPage(1);
    setSelectedWorkIds([]);
  }, [clientId, debouncedSearch, executorId, sentFilter]);

  const deliveryQuery = useDeliveryQuery({
    page,
    page_size: 10,
    search: debouncedSearch || undefined,
    client_id: clientId || undefined,
    executor_id: executorId || undefined,
    sent: sentFilter === "all" ? undefined : sentFilter === "sent"
  });

  const clientsQuery = useClientsQuery({ page: 1, page_size: 100 });
  const executorsQuery = useExecutorsQuery({ page: 1, page_size: 100 });

  return {
    clientId,
    clientsQuery,
    deliveryQuery,
    detailOpened,
    executorId,
    executorsQuery,
    page,
    search,
    selectedWorkId,
    selectedWorkIds,
    sentFilter,
    setClientId,
    setExecutorId,
    setPage,
    setSearch,
    setSentFilter,
    clearSelection() {
      setSelectedWorkIds([]);
    },
    closeDetail() {
      setSelectedWorkId(undefined);
      detailHandlers.close();
    },
    isSelected(workId: string) {
      return selectedWorkIds.includes(workId);
    },
    openView(workId: string) {
      setSelectedWorkId(workId);
      detailHandlers.open();
    },
    toggleSelected(workId: string) {
      setSelectedWorkIds((current) =>
        current.includes(workId) ? current.filter((id) => id !== workId) : [...current, workId]
      );
    },
    toggleSelectAll(workIds: string[]) {
      const allSelected = workIds.length > 0 && workIds.every((workId) => selectedWorkIds.includes(workId));
      setSelectedWorkIds(allSelected ? [] : workIds);
    }
  };
}
