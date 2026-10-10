"use client";

import { usePathname, useSearchParams } from "next/navigation";
import { useEffect } from "react";

import { capturePageview } from "@/lib/posthog/client";

export function PostHogPageView() {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  useEffect(() => {
    if (!pathname) {
      return;
    }
    const query = searchParams?.toString();
    const path = query ? `${pathname}?${query}` : pathname;
    capturePageview(path);
  }, [pathname, searchParams]);

  return null;
}
