import Link from "next/link";
import {
  Brain,
  Cloud,
  Database,
  Shield,
  Sparkles,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const techBadges = [
  "Next.js",
  "FastAPI",
  "Gemini",
  "Firebase",
  "Cloud Run",
  "Tailwind",
];

export default function HomePage() {
  return (
    <main className="flex-1">
      <section className="mx-auto max-w-5xl px-4 py-16 sm:px-6 sm:py-24">
        <div className="space-y-6 text-center">
          <Badge variant="secondary" className="mx-auto">
            Google-native AI hackathon starter
          </Badge>
          <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
            PROJECT_NAME
          </h1>
          <p className="text-xl text-muted-foreground">PROJECT_TAGLINE</p>
          <p className="mx-auto max-w-2xl text-muted-foreground">
            PROJECT_DESCRIPTION — A flexible foundation for healthcare,
            education, sustainability, accessibility, or social-good AI apps.
            Customize the problem statement and workflows after your team picks a
            track.
          </p>
          <div className="flex flex-wrap justify-center gap-2 pt-2">
            {techBadges.map((label) => (
              <Badge key={label} variant="outline">
                {label}
              </Badge>
            ))}
          </div>
          <div className="pt-4">
            <Link
              href="/dashboard"
              className={cn(buttonVariants({ size: "lg" }))}
            >
              Get Started
            </Link>
          </div>
        </div>
      </section>

      <section className="border-t bg-muted/30">
        <div className="mx-auto grid max-w-5xl gap-8 px-4 py-16 sm:grid-cols-2 sm:px-6 lg:grid-cols-4">
          <Feature
            icon={Sparkles}
            title="AI layer"
            description="Gemini via a backend service—swap models with GEMINI_MODEL."
          />
          <Feature
            icon={Shield}
            title="Secure by default"
            description="API keys stay on the server. Optional Firebase Auth."
          />
          <Feature
            icon={Database}
            title="Firebase ready"
            description="Firestore and Storage abstractions for your data model."
          />
          <Feature
            icon={Cloud}
            title="Cloud deploy"
            description="Dockerized API for Cloud Run; frontend for Firebase Hosting."
          />
        </div>
      </section>

      <section className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
        <h2 className="text-2xl font-semibold text-center mb-6">
          How it works
        </h2>
        <ol className="space-y-4 text-muted-foreground">
          <li className="flex gap-3">
            <Brain className="size-5 shrink-0 text-primary" />
            <span>
              Users interact with the Next.js dashboard (text + file upload).
            </span>
          </li>
          <li className="flex gap-3">
            <Cloud className="size-5 shrink-0 text-primary" />
            <span>
              The frontend calls your FastAPI backend on Cloud Run (or locally).
            </span>
          </li>
          <li className="flex gap-3">
            <Sparkles className="size-5 shrink-0 text-primary" />
            <span>
              The backend calls Gemini, and can persist data to Firebase when you
              implement it.
            </span>
          </li>
        </ol>
      </section>
    </main>
  );
}

function Feature({
  icon: Icon,
  title,
  description,
}: {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  description: string;
}) {
  return (
    <div className="space-y-2">
      <Icon className="size-8 text-primary" />
      <h3 className="font-semibold">{title}</h3>
      <p className="text-sm text-muted-foreground">{description}</p>
    </div>
  );
}
