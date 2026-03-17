"use client";

import { ActionIcon, Button, Group, Stack, Text } from "@mantine/core";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { IconPaperclip, IconTrash } from "@tabler/icons-react";
import { ChangeEvent } from "react";

import { deleteWorkAttachment, uploadWorkAttachment } from "@/entities/works/api/works-api";
import { WorkAttachment } from "@/entities/works/model/types";
import { worksQueryKeys } from "@/entities/works/model/query-keys";
import { formatDateTime } from "@/shared/lib/formatters/format-date";
import { showErrorNotification } from "@/shared/lib/notifications/show-error";
import { showSuccessNotification } from "@/shared/lib/notifications/show-success";

type WorkAttachmentsSectionProps = {
  workId: string;
  attachments: WorkAttachment[];
};

function formatAttachmentSize(fileSize: number) {
  return `${(fileSize / 1024 / 1024).toFixed(2)} МБ`;
}

export function WorkAttachmentsSection({ workId, attachments }: WorkAttachmentsSectionProps) {
  const queryClient = useQueryClient();

  const uploadMutation = useMutation({
    mutationFn: async (files: File[]) => {
      for (const file of files) {
        await uploadWorkAttachment(workId, file);
      }
    },
    onSuccess() {
      queryClient.invalidateQueries({ queryKey: worksQueryKeys.root });
      showSuccessNotification("Вложения загружены.");
    },
    onError(error) {
      showErrorNotification(error, "Не удалось загрузить вложение.");
    }
  });

  const deleteMutation = useMutation({
    mutationFn: (attachmentId: string) => deleteWorkAttachment(workId, attachmentId),
    onSuccess() {
      queryClient.invalidateQueries({ queryKey: worksQueryKeys.root });
      showSuccessNotification("Вложение удалено.");
    },
    onError(error) {
      showErrorNotification(error, "Не удалось удалить вложение.");
    }
  });

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const nextFiles = Array.from(event.target.files ?? []);
    if (!nextFiles.length) {
      return;
    }

    const tooLargeFile = nextFiles.find((file) => file.size > 2 * 1024 * 1024);
    if (tooLargeFile) {
      showErrorNotification(new Error("Размер файла не должен превышать 2 МБ."), "Файл слишком большой.");
      event.target.value = "";
      return;
    }

    uploadMutation.mutate(nextFiles);
    event.target.value = "";
  }

  return (
    <Stack gap="sm">
      <Group justify="space-between" align="center">
        <div>
          <Text fw={700}>Вложения</Text>
          <Text c="dimmed" size="sm">
            Изображения, PDF, Word и Excel до 2 МБ.
          </Text>
        </div>
        <Button component="label" leftSection={<IconPaperclip size={16} />} loading={uploadMutation.isPending} variant="light">
          Добавить файлы
          <input
            hidden
            multiple
            accept=".jpg,.jpeg,.png,.webp,.gif,.pdf,.doc,.docx,.xls,.xlsx"
            type="file"
            onChange={handleFileChange}
          />
        </Button>
      </Group>

      {attachments.length ? (
        attachments.map((attachment) => (
          <div key={attachment.id} className="rounded-[20px] bg-slate-50 px-4 py-3">
            <Group justify="space-between" align="start" wrap="nowrap">
              <div className="min-w-0">
                <a
                  className="block truncate text-sm font-semibold text-slate-900 underline-offset-4 hover:underline"
                  href={attachment.download_url}
                  rel="noreferrer"
                  target="_blank"
                >
                  {attachment.file_name}
                </a>
                <Text c="dimmed" size="sm">
                  {formatAttachmentSize(attachment.file_size)}
                  {attachment.uploaded_by_email ? ` · ${attachment.uploaded_by_email}` : ""}
                  {attachment.created_at ? ` · ${formatDateTime(attachment.created_at)}` : ""}
                </Text>
              </div>
              <ActionIcon
                color="red"
                loading={deleteMutation.isPending && deleteMutation.variables === attachment.id}
                variant="subtle"
                onClick={() => deleteMutation.mutate(attachment.id)}
              >
                <IconTrash size={16} />
              </ActionIcon>
            </Group>
          </div>
        ))
      ) : (
        <Text c="dimmed">Файлы к работе пока не прикреплены.</Text>
      )}
    </Stack>
  );
}
