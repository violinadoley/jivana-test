"use client";

import posthog from "posthog-js";

import {
  isPostHogEnabled,
  postHogHost,
  sessionReplayEnabled,
} from "@/lib/posthog/config";

let initialized = false;

export function initPostHog(): void {
  if (initialized || !isPostHogEnabled() || typeof window === "undefined") {
    return;
  }
  const key = process.env.NEXT_PUBLIC_POSTHOG_KEY?.trim();
  if (!key) {
    return;
  }

  posthog.init(key, {
    api_host: postHogHost(),
    person_profiles: "identified_only",
    capture_pageview: false,
    disable_session_recording: !sessionReplayEnabled(),
    persistence: "localStorage+cookie",
    autocapture: false,
    session_recording: sessionReplayEnabled()
      ? {
          maskAllInputs: true,
          maskTextSelector: "[data-ph-mask]",
        }
      : undefined,
  });
  initialized = true;
}

export function identifyPostHogUser(distinctId: string): void {
  if (!isPostHogEnabled()) {
    return;
  }
  initPostHog();
  posthog.identify(distinctId);
}

export function resetPostHogUser(): void {
  if (!isPostHogEnabled()) {
    return;
  }
  posthog.reset();
}

export function capturePageview(path: string): void {
  if (!isPostHogEnabled()) {
    return;
  }
  initPostHog();
  posthog.capture("$pageview", { $current_url: path });
}
