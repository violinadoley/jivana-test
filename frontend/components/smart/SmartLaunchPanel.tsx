"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";

import { SiteHeader } from "@/components/layout/site-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader } from "@/components/ui/card";

export function SmartLaunchPanel() {
  const params = useSearchParams();
  const iss = params.get("iss");
  const launch = params.get("launch");

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <SiteHeader />
      <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col justify-center gap-6 px-4 py-12">
        <Card>
          <CardHeader>
            <h1 className="font-heading text-base leading-snug font-medium group-data-[size=sm]/card:text-sm">
              SMART on FHIR launch
            </h1>
            <CardDescription>
              EHR sandbox entry point for JIVANA. Configure OAuth client ids in production; this
              page confirms launch context and opens the workspace.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 text-sm">
            <dl className="grid gap-2 rounded-md border border-border bg-muted/30 p-4">
              <div>
                <dt className="font-medium text-foreground">ISS (FHIR server)</dt>
                <dd className="break-all text-muted-foreground">{iss ?? "— not provided —"}</dd>
              </div>
              <div>
                <dt className="font-medium text-foreground">Launch token</dt>
                <dd className="break-all text-muted-foreground">{launch ?? "— not provided —"}</dd>
              </div>
            </dl>
            <Button render={<Link href="/dashboard" />}>Open JIVANA workspace</Button>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
