"use client";

import { Loading03Icon, Tick02Icon } from "@hugeicons/core-free-icons";
import { useEffect, useState } from "react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { HugeIcon } from "@/components/ui/huge-icon";
import { fetchPlatformCapabilities } from "@/lib/api";
import type { PlatformCapabilities } from "@/types/enterprise";

const FALLBACK: PlatformCapabilities = {
  environment: "local",
  capabilities: [
    {
      id: "vertex_gemini",
      label: "Gemini on Vertex AI",
      configured: true,
      description: "Copilot, meetings, research, workflows.",
    },
    {
      id: "document_ai",
      label: "Document AI",
      configured: false,
      description: "Set DOCUMENT_AI_PROCESSOR_ID on the API.",
    },
    {
      id: "firestore",
      label: "Firestore",
      configured: false,
      description: "Activity feed and sessions when Firebase is configured.",
    },
    {
      id: "vertex_search",
      label: "Vertex AI Search",
      configured: false,
      description: "Set VERTEX_SEARCH_DATA_STORE_ID on the API.",
    },
  ],
};

export function PlatformCapabilitiesPanel() {
  const [data, setData] = useState<PlatformCapabilities | null>(null);
  const [loading, setLoading] = useState(true);
  const [usedFallback, setUsedFallback] = useState(false);

  useEffect(() => {
    void fetchPlatformCapabilities()
      .then(setData)
      .catch(() => {
        setData(FALLBACK);
        setUsedFallback(true);
      })
      .finally(() => setLoading(false));
  }, []);

  const view = data ?? FALLBACK;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Google Cloud integrations</CardTitle>
        <CardDescription>
          Live status from your API ({view.environment}
          {usedFallback ? " · showing defaults—start backend or set API URL" : ""}).
        </CardDescription>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <HugeIcon icon={Loading03Icon} size={18} className="animate-spin" />
            Checking capabilities…
          </div>
        ) : (
          <ul className="space-y-2">
            {view.capabilities.map((cap) => (
              <li
                key={cap.id}
                className="flex gap-3 rounded-xl border border-border bg-background px-3 py-3 text-sm"
              >
                <HugeIcon
                  icon={Tick02Icon}
                  size={20}
                  className={cap.configured ? "shrink-0 text-primary" : "shrink-0 text-muted-foreground/35"}
                />
                <div className="min-w-0">
                  <p className="font-medium">{cap.label}</p>
                  <p className="text-xs text-muted-foreground">{cap.description}</p>
                </div>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
