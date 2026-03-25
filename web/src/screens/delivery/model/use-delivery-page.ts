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
  const [sortBy, setSortBy] = useState<"deadline_at" | "client_name" | "received_at">("deadline_at");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("asc");
  const [page, setPage] = useState(1);
  const [selectedNaradIds, setSelectedNaradIds] = useState<string[]>([]);
  const [selectedNaradId, setSelectedNaradId] = useState<string>();
  const [debouncedSearch] = useDebouncedValue(search, 300);
  const [detailOpened, detailHandlers] = useDisclosure(false);

  useEffect(() => {
    setPage(1);
    setSelectedNaradIds([]);
  }, [clientId, debouncedSearch, executorId, sentFilter, sortBy, sortDirection]);

  const deliveryQuery = useDeliveryQuery({
    page,
    page_size: 10,
    search: debouncedSearch || undefined,
    client_id: clientId || undefined,
    executor_id: executorId || undefined,
    sent: sentFilter === "all" ? undefined : sentFilter === "sent",
    sort_by: sortBy,
    sort_direction: sortDirection
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
    selectedNaradId,
    selectedNaradIds,
    sentFilter,
    sortBy,
    sortDirection,
    setClientId,
    setExecutorId,
    setPage,
    setSearch,
    setSentFilter,
    setSortBy,
    setSortDirection,
    clearSelection() {
      setSelectedNaradIds([]);
    },
    closeDetail() {
      setSelectedNaradId(undefined);
      detailHandlers.close();
    },
    isSelected(naradId: string) {
      return selectedNaradIds.includes(naradId);
    },
    openView(naradId: string) {
      setSelectedNaradId(naradId);
      detailHandlers.open();
    },
    toggleSelected(naradId: string) {
      setSelectedNaradIds((current) =>
        current.includes(naradId) ? current.filter((id) => id !== naradId) : [...current, naradId]
      );
    },
    toggleSelectAll(naradIds: string[]) {
      const allSelected = naradIds.length > 0 && naradIds.every((naradId) => selectedNaradIds.includes(naradId));
      setSelectedNaradIds(allSelected ? [] : naradIds);
    }
  };
}
