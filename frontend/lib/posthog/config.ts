export type WorkflowType =
  | "dashboard"
  | "ai_chat"
  | "file_upload"
  | "meddocs_reconciliation";

export function isPostHogEnabled(): boolean {
  const key = process.env.NEXT_PUBLIC_POSTHOG_KEY?.trim();
  if (!key) {
    return false;
  }
  const flag = process.env.NEXT_PUBLIC_POSTHOG_ENABLED?.toLowerCase();
  if (flag === "false" || flag === "0") {
    return false;
  }
  return true;
}

export function postHogHost(): string {
  return (
    process.env.NEXT_PUBLIC_POSTHOG_HOST?.trim() || "https://us.i.posthog.com"
  );
}

export function postHogEnvironment(): string {
  return process.env.NEXT_PUBLIC_APP_ENV?.trim() || "development";
}

export function sessionReplayEnabled(): boolean {
  return process.env.NEXT_PUBLIC_POSTHOG_SESSION_REPLAY === "true";
}
