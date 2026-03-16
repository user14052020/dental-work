import { TextInput, TextInputProps } from "@mantine/core";
import { IconSearch } from "@tabler/icons-react";

export function SearchField(props: TextInputProps) {
  return <TextInput leftSection={<IconSearch size={16} />} placeholder="Поиск" {...props} />;
}
