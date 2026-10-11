"use client";

import { Login01Icon, Logout01Icon } from "@hugeicons/core-free-icons";

import { Button } from "@/components/ui/button";
import { HugeIcon } from "@/components/ui/huge-icon";
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
        Sign in
      </Button>
    );
  }

  if (user) {
    return (
      <Button variant="outline" size="sm" onClick={() => logout()}>
        <HugeIcon icon={Logout01Icon} size={16} className="mr-2" />
        Sign out
      </Button>
    );
  }

  return (
    <Button size="sm" onClick={() => loginWithGoogle().catch(console.error)}>
      <HugeIcon icon={Login01Icon} size={16} className="mr-2" />
      Sign in
    </Button>
  );
}
