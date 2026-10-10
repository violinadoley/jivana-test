"use client";

import { LogIn, LogOut } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/AuthContext";

export function LoginButton() {
  const { user, loading, configured, loginWithGoogle, logout } = useAuth();

  if (loading) {
    return (
      <Button variant="outline" size="sm" disabled>
        Loading…
      </Button>
    );
  }

  if (!configured) {
    return (
      <Button variant="outline" size="sm" disabled title="Configure Firebase env vars">
        Sign in (Firebase not configured)
      </Button>
    );
  }

  if (user) {
    return (
      <Button variant="outline" size="sm" onClick={() => logout()}>
        <LogOut className="mr-2 size-4" />
        Sign out
      </Button>
    );
  }

  return (
    <Button size="sm" onClick={() => loginWithGoogle().catch(console.error)}>
      <LogIn className="mr-2 size-4" />
      Sign in
    </Button>
  );
}
