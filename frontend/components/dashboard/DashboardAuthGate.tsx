"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { useAuth } from "@/contexts/AuthContext";

export function DashboardAuthGate({ children }: { children: React.ReactNode }) {
  const { authRequired, configured, loading, user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!authRequired || loading) {
      return;
    }
    if (!configured) {
      return;
    }
    if (!user) {
      router.replace("/");
    }
  }, [authRequired, configured, loading, user, router]);

  if (authRequired && configured && !loading && !user) {
    return (
      <div className="flex min-h-screen items-center justify-center text-muted-foreground">
        Sign in required…
      </div>
    );
  }

  return <>{children}</>;
}
