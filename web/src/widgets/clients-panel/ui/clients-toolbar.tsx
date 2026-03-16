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
    <Group justify="space-between">
      <SearchField
        className="flex-1"
        placeholder="Поиск по названию, контактам, эл. почте, телефону, адресу"
        value={search}
        onChange={(event) => onSearchChange(event.currentTarget.value)}
      />
      <Button leftSection={<IconPlus size={16} />} onClick={onCreate}>
        Новый клиент
      </Button>
    </Group>
  );
}
