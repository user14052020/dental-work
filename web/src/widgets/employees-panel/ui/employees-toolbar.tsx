import { Button, Group, Switch } from "@mantine/core";
import { IconPlus } from "@tabler/icons-react";

import { SearchField } from "@/shared/ui/search-field";

type EmployeesToolbarProps = {
  search: string;
  includeFired: boolean;
  onSearchChange: (value: string) => void;
  onIncludeFiredChange: (value: boolean) => void;
  onCreate: () => void;
};

export function EmployeesToolbar({
  search,
  includeFired,
  onSearchChange,
  onIncludeFiredChange,
  onCreate
}: EmployeesToolbarProps) {
  return (
    <Group justify="space-between" align="end" className="w-full flex-col md:flex-row">
      <Group className="w-full flex-1 flex-col md:flex-row md:items-end">
        <SearchField
          className="w-full md:flex-1"
          placeholder="Поиск по сотруднику, должности, почте или привязанному технику"
          value={search}
          onChange={(event) => onSearchChange(event.currentTarget.value)}
        />
        <Switch
          checked={includeFired}
          label="Показывать уволенных"
          onChange={(event) => onIncludeFiredChange(event.currentTarget.checked)}
        />
      </Group>
      <Button leftSection={<IconPlus size={16} />} onClick={onCreate} className="w-full md:w-auto">
        Новый сотрудник
      </Button>
    </Group>
  );
}
