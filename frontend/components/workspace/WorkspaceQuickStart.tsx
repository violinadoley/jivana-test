"use client";

import {
  AiBrain01Icon,
  FileSearchIcon,
  MeetingRoomIcon,
  Search01Icon,
  SparklesIcon,
  WorkflowSquare01Icon,
} from "@hugeicons/core-free-icons";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { HugeIcon } from "@/components/ui/huge-icon";
import { solutionPillars } from "@/lib/brand";
import { cn } from "@/lib/utils";

const pillarIcons = [
  FileSearchIcon,
  Search01Icon,
  AiBrain01Icon,
  MeetingRoomIcon,
  SparklesIcon,
  WorkflowSquare01Icon,
] as const;

type Props = {
  onNavigate: (tab: string) => void;
};

const tabByPillar = [
  "documents",
  "search",
  "copilot",
  "meetings",
  "research",
  "workflows",
] as const;

export function WorkspaceQuickStart({ onNavigate }: Props) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Start here</CardTitle>
        <CardDescription>
          Open discharge med rec first, or jump to search, meetings, and other workspace tools.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ul className="grid gap-3 sm:grid-cols-2">
          {solutionPillars.map((pillar, index) => (
            <li key={pillar.title}>
              <button
                type="button"
                onClick={() => onNavigate(tabByPillar[index] ?? "overview")}
                className={cn(
                  "group h-full w-full rounded-xl border border-border bg-background p-4 text-left",
                  "transition-colors hover:border-primary/25 hover:bg-muted/40"
                )}
              >
                <HugeIcon
                  icon={pillarIcons[index] ?? AiBrain01Icon}
                  size={20}
                  className="text-primary"
                />
                <p className="mt-3 text-sm font-medium text-foreground">{pillar.title}</p>
                <p className="mt-1 text-xs leading-relaxed text-muted-foreground">
                  {pillar.description}
                </p>
              </button>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
