import { Button, Group, Switch } from "@mantine/core";
import { IconPlus } from "@tabler/icons-react";

import { SearchField } from "@/shared/ui/search-field";

type MaterialsToolbarProps = {
  search: string;
  lowStockOnly: boolean;
  onSearchChange: (value: string) => void;
  onLowStockChange: (value: boolean) => void;
  onCreate: () => void;
};

export function MaterialsToolbar({
  search,
  lowStockOnly,
  onSearchChange,
  onLowStockChange,
  onCreate
}: MaterialsToolbarProps) {
  return (
    <Group justify="space-between" className="w-full flex-col md:flex-row md:items-end">
      <SearchField
        className="w-full md:flex-1"
        placeholder="Поиск по названию, категории, единице, поставщику, комментарию"
        value={search}
        onChange={(event) => onSearchChange(event.currentTarget.value)}
      />
      <Switch
        className="w-full md:w-auto"
        checked={lowStockOnly}
        label="Низкий остаток"
        onChange={(event) => onLowStockChange(event.currentTarget.checked)}
      />
      <Button leftSection={<IconPlus size={16} />} onClick={onCreate} className="w-full md:w-auto">
        Новый материал
      </Button>
    </Group>
  );
}
