import { Button, Group, TextInput } from "@mantine/core";
import { IconPlus } from "@tabler/icons-react";

import { SearchField } from "@/shared/ui/search-field";

type InventoryAdjustmentsToolbarProps = {
  search: string;
  dateFrom: string;
  dateTo: string;
  onSearchChange: (value: string) => void;
  onDateFromChange: (value: string) => void;
  onDateToChange: (value: string) => void;
  onCreate: () => void;
};

export function InventoryAdjustmentsToolbar({
  search,
  dateFrom,
  dateTo,
  onSearchChange,
  onDateFromChange,
  onDateToChange,
  onCreate
}: InventoryAdjustmentsToolbarProps) {
  return (
    <Group align="end" wrap="wrap" className="w-full">
      <SearchField
        className="w-full md:flex-1"
        label="Поиск"
        placeholder="Поиск по номеру инвентаризации или комментарию"
        value={search}
        onChange={(event) => onSearchChange(event.currentTarget.value)}
      />
      <TextInput
        className="w-full md:max-w-[180px]"
        label="С даты"
        type="date"
        value={dateFrom}
        onChange={(event) => onDateFromChange(event.currentTarget.value)}
      />
      <TextInput
        className="w-full md:max-w-[180px]"
        label="По дату"
        type="date"
        value={dateTo}
        onChange={(event) => onDateToChange(event.currentTarget.value)}
      />
      <Button leftSection={<IconPlus size={16} />} onClick={onCreate} className="w-full md:w-auto">
        Новая инвентаризация
      </Button>
    </Group>
  );
}
