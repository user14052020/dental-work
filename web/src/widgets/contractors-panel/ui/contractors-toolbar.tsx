import { Button, Group, Switch } from "@mantine/core";
import { IconPlus } from "@tabler/icons-react";

import { SearchField } from "@/shared/ui/search-field";

type ContractorsToolbarProps = {
  search: string;
  activeOnly: boolean;
  onSearchChange: (value: string) => void;
  onActiveOnlyChange: (value: boolean) => void;
  onCreate: () => void;
};

export function ContractorsToolbar({
  search,
  activeOnly,
  onSearchChange,
  onActiveOnlyChange,
  onCreate
}: ContractorsToolbarProps) {
  return (
    <Group justify="space-between" className="w-full flex-col md:flex-row md:items-end">
      <SearchField
        className="w-full md:flex-1"
        placeholder="Поиск по названию, контакту, телефону, email, адресу и комментарию"
        value={search}
        onChange={(event) => onSearchChange(event.currentTarget.value)}
      />
      <Switch
        className="w-full md:w-auto"
        checked={activeOnly}
        label="Только активные"
        onChange={(event) => onActiveOnlyChange(event.currentTarget.checked)}
      />
      <Button leftSection={<IconPlus size={16} />} onClick={onCreate} className="w-full md:w-auto">
        Новый подрядчик
      </Button>
    </Group>
  );
}
