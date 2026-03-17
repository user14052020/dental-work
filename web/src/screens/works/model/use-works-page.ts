"use client";

import { useDebouncedValue, useDisclosure } from "@mantine/hooks";
import { useEffect, useState } from "react";

import { useClientsQuery } from "@/entities/clients/model/use-clients-query";
import { useExecutorsQuery } from "@/entities/executors/model/use-executors-query";
import { WorkCompact } from "@/entities/works/model/types";
import { useWorksQuery } from "@/entities/works/model/use-works-query";

function toIsoDate(value: string) {
  return value ? new Date(value).toISOString() : undefined;
}

export function useWorksPage() {
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [clientId, setClientId] = useState("");
  const [executorId, setExecutorId] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [page, setPage] = useState(1);
  const [selectedWork, setSelectedWork] = useState<WorkCompact | null>(null);
  const [statusWork, setStatusWork] = useState<WorkCompact | null>(null);
  const [lifecycleMode, setLifecycleMode] = useState<"close" | "reopen" | null>(null);
  const [lifecycleWork, setLifecycleWork] = useState<WorkCompact | null>(null);
  const [debouncedSearch] = useDebouncedValue(search, 300);
  const [detailOpened, detailHandlers] = useDisclosure(false);
  const [formOpened, formHandlers] = useDisclosure(false);
  const [statusOpened, statusHandlers] = useDisclosure(false);
  const [lifecycleOpened, lifecycleHandlers] = useDisclosure(false);

  useEffect(() => {
    setPage(1);
  }, [clientId, dateFrom, dateTo, debouncedSearch, executorId, status]);

  const worksQuery = useWorksQuery({
    page,
    page_size: 10,
    search: debouncedSearch || undefined,
    status: status || undefined,
    client_id: clientId || undefined,
    executor_id: executorId || undefined,
    date_from: toIsoDate(dateFrom),
    date_to: toIsoDate(dateTo)
  });

  const clientsQuery = useClientsQuery({ page: 1, page_size: 100 });
  const executorsQuery = useExecutorsQuery({ page: 1, page_size: 100 });

  return {
    clientId,
    clientsQuery,
    dateFrom,
    dateTo,
    detailOpened,
    executorId,
    executorsQuery,
    formOpened,
    lifecycleMode,
    lifecycleOpened,
    lifecycleWork,
    page,
    search,
    selectedWork,
    setClientId,
    setDateFrom,
    setDateTo,
    setExecutorId,
    setPage,
    setSearch,
    setStatus,
    status,
    statusOpened,
    statusWork,
    worksQuery,
    openCreate() {
      formHandlers.open();
    },
    openView(work: WorkCompact) {
      setSelectedWork(work);
      detailHandlers.open();
    },
    openStatus(work: WorkCompact) {
      setStatusWork(work);
      statusHandlers.open();
    },
    closeCreate() {
      formHandlers.close();
    },
    closeDetail() {
      setSelectedWork(null);
      detailHandlers.close();
    },
    closeStatus() {
      setStatusWork(null);
      statusHandlers.close();
    },
    openLifecycle(mode: "close" | "reopen", work: WorkCompact) {
      setLifecycleMode(mode);
      setLifecycleWork(work);
      lifecycleHandlers.open();
    },
    closeLifecycle() {
      setLifecycleMode(null);
      setLifecycleWork(null);
      lifecycleHandlers.close();
    }
  };
}
