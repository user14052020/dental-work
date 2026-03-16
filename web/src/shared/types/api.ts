export type ApiErrorShape = {
  error?: {
    code?: string;
    message?: string;
    details?: Record<string, unknown>;
    request_id?: string;
    timestamp?: string;
  };
};

export type PageMeta = {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
};

export type PaginatedResponse<TItem> = {
  items: TItem[];
  meta: PageMeta;
};
