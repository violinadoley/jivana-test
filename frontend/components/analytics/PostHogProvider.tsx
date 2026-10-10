"use client";

import posthog from "posthog-js";
import { PostHogProvider as PHProvider } from "posthog-js/react";
import { useEffect } from "react";

import { initPostHog } from "@/lib/posthog/client";
import { isPostHogEnabled } from "@/lib/posthog/config";

export function PostHogProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    initPostHog();
  }, []);

  if (!isPostHogEnabled()) {
    return <>{children}</>;
  }

  if (typeof window !== "undefined") {
    initPostHog();
  }

  return <PHProvider client={posthog}>{children}</PHProvider>;
}
