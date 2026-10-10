"use client";

import { useEffect, useRef } from "react";

import { trackWorkflowStarted } from "@/lib/posthog/events";

export function DashboardWorkflowTracker() {
  const fired = useRef(false);

  useEffect(() => {
    if (fired.current) {
      return;
    }
    fired.current = true;
    trackWorkflowStarted("dashboard");
  }, []);

  return null;
}
