"use client";

import { Suspense } from "react";

import { PostHogPageView } from "@/components/analytics/PostHogPageView";
import { PostHogProvider } from "@/components/analytics/PostHogProvider";
import { AuthProvider } from "@/contexts/AuthContext";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <PostHogProvider>
      <Suspense fallback={null}>
        <PostHogPageView />
      </Suspense>
      <AuthProvider>{children}</AuthProvider>
    </PostHogProvider>
  );
}
