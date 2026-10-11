"use client";

import { Search01Icon } from "@hugeicons/core-free-icons";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { HugeIcon } from "@/components/ui/huge-icon";
import { enterpriseSearch } from "@/lib/api";
import type { EnterpriseSearchResponse } from "@/types/enterprise";

export function EnterpriseSearchPanel() {
  const [query, setQuery] = useState("medication reconciliation policy");
  const [data, setData] = useState<EnterpriseSearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function runSearch() {
    setLoading(true);
    setError(null);
    try {
      setData(await enterpriseSearch(query.trim()));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Intelligent search</CardTitle>
        <CardDescription>
          Search SOPs, playbooks, and institutional knowledge in one place.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex gap-2">
          <Input value={query} onChange={(e) => setQuery(e.target.value)} />
          <Button onClick={() => void runSearch()} disabled={loading}>
            <HugeIcon icon={Search01Icon} size={16} />
          </Button>
        </div>
        {error && <p className="text-sm text-destructive">{error}</p>}
        {data && (
          <p className="text-xs text-muted-foreground">
            {data.vertex_search_configured
              ? "Results from your managed search index and internal library."
              : "Results from your internal policy library."}
          </p>
        )}
        <ul className="space-y-3 text-sm">
          {data?.results.map((hit, i) => (
            <li key={i} className="border border-border p-3">
              <p className="font-medium">{hit.title}</p>
              <p className="mt-1 text-muted-foreground">{hit.snippet}</p>
              <p className="mt-1 text-xs text-primary">{hit.source}</p>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
