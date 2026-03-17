"use client";

import { useDebouncedValue, useDisclosure } from "@mantine/hooks";
import { useEffect, useState } from "react";

import {
  ExecutorCategory,
  OperationCatalog
} from "@/entities/operations/model/types";
import {
  useOperationCategoriesQuery,
  useOperationsQuery
} from "@/entities/operations/model/use-operations-query";

export function useOperationsPage() {
  const [search, setSearch] = useState("");
  const [activeOnly, setActiveOnly] = useState(true);
  const [page, setPage] = useState(1);
  const [editedCategory, setEditedCategory] = useState<ExecutorCategory | null>(null);
  const [editedOperation, setEditedOperation] = useState<OperationCatalog | null>(null);
  const [debouncedSearch] = useDebouncedValue(search, 300);
  const [categoryFormOpened, categoryFormHandlers] = useDisclosure(false);
  const [operationFormOpened, operationFormHandlers] = useDisclosure(false);

  useEffect(() => {
    setPage(1);
  }, [activeOnly, debouncedSearch]);

  const categoriesQuery = useOperationCategoriesQuery({
    page: 1,
    page_size: 100,
    active_only: undefined
  });

  const operationsQuery = useOperationsQuery({
    page,
    page_size: 10,
    search: debouncedSearch || undefined,
    active_only: activeOnly || undefined
  });

  return {
    activeOnly,
    categoriesQuery,
    categoryFormOpened,
    editedCategory,
    editedOperation,
    operationFormOpened,
    operationsQuery,
    page,
    search,
    setActiveOnly,
    setPage,
    setSearch,
    openCreateCategory() {
      setEditedCategory(null);
      categoryFormHandlers.open();
    },
    openEditCategory(category: ExecutorCategory) {
      setEditedCategory(category);
      categoryFormHandlers.open();
    },
    openCreateOperation() {
      setEditedOperation(null);
      operationFormHandlers.open();
    },
    openEditOperation(operation: OperationCatalog) {
      setEditedOperation(operation);
      operationFormHandlers.open();
    },
    closeCategoryForm() {
      setEditedCategory(null);
      categoryFormHandlers.close();
    },
    closeOperationForm() {
      setEditedOperation(null);
      operationFormHandlers.close();
    }
  };
}
