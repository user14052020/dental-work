"use client";

import { useDebouncedValue, useDisclosure } from "@mantine/hooks";
import { useEffect, useState } from "react";

import { Material } from "@/entities/materials/model/types";
import { useMaterialsQuery } from "@/entities/materials/model/use-materials-query";

export function useMaterialsPage() {
  const [search, setSearch] = useState("");
  const [lowStockOnly, setLowStockOnly] = useState(false);
  const [page, setPage] = useState(1);
  const [selectedMaterial, setSelectedMaterial] = useState<Material | null>(null);
  const [editedMaterial, setEditedMaterial] = useState<Material | null>(null);
  const [consumedMaterial, setConsumedMaterial] = useState<Material | null>(null);
  const [debouncedSearch] = useDebouncedValue(search, 300);
  const [detailOpened, detailHandlers] = useDisclosure(false);
  const [formOpened, formHandlers] = useDisclosure(false);
  const [consumeOpened, consumeHandlers] = useDisclosure(false);

  useEffect(() => {
    setPage(1);
  }, [debouncedSearch, lowStockOnly]);

  const materialsQuery = useMaterialsQuery({
    page,
    page_size: 10,
    search: debouncedSearch || undefined,
    low_stock_only: lowStockOnly
  });

  return {
    consumedMaterial,
    consumeOpened,
    detailOpened,
    editedMaterial,
    formOpened,
    lowStockOnly,
    materialsQuery,
    page,
    search,
    selectedMaterial,
    setLowStockOnly,
    setPage,
    setSearch,
    openCreate() {
      setEditedMaterial(null);
      formHandlers.open();
    },
    openEdit(material: Material) {
      setEditedMaterial(material);
      formHandlers.open();
    },
    openView(material: Material) {
      setSelectedMaterial(material);
      detailHandlers.open();
    },
    openConsume(material: Material) {
      setConsumedMaterial(material);
      consumeHandlers.open();
    },
    closeForm() {
      setEditedMaterial(null);
      formHandlers.close();
    },
    closeDetail() {
      setSelectedMaterial(null);
      detailHandlers.close();
    },
    closeConsume() {
      setConsumedMaterial(null);
      consumeHandlers.close();
    }
  };
}
