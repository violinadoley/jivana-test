export type ApiErrorBody = {
  success: false;
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
};

export type GenerateAIResponse = {
  success: true;
  response: string;
};

export type FileUploadResponse = {
  success: true;
  filename: string;
  content_type: string;
  size_bytes: number;
  storage_key: string | null;
};

export type ActivityType = "ai_generate" | "file_upload";

export type ActivityItem = {
  id: string;
  type: ActivityType;
  title: string;
  summary?: string | null;
  user_id?: string | null;
  created_at?: string | null;
};

export type ActivityListResponse = {
  success: true;
  items: ActivityItem[];
};
