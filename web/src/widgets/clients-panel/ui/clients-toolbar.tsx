import { Button, Group } from "@mantine/core";
import { IconPlus } from "@tabler/icons-react";

import { SearchField } from "@/shared/ui/search-field";

type ClientsToolbarProps = {
  search: string;
  onSearchChange: (value: string) => void;
  onCreate: () => void;
};

export function ClientsToolbar({ search, onSearchChange, onCreate }: ClientsToolbarProps) {
  return (
    <Group justify="space-between" className="w-full flex-col md:flex-row md:items-end">
      <SearchField
        className="w-full md:flex-1"
        placeholder="Поиск по названию, адресу, ИНН, КПП, договору и счетам"
        value={search}
        onChange={(event) => onSearchChange(event.currentTarget.value)}
      />
      <Button leftSection={<IconPlus size={16} />} onClick={onCreate} className="w-full md:w-auto">
        Новый клиент
      </Button>
    </Group>
  );
}
