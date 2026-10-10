"use client";

import Link from "next/link";

import { LoginButton } from "@/components/auth/LoginButton";
import { JivanaLogo } from "@/components/brand/jivana-logo";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useAuth } from "@/contexts/AuthContext";

export function DashboardHeader() {
  const { user } = useAuth();
  const initials = user?.email?.slice(0, 2).toUpperCase() ?? "GU";

  return (
    <header className="sticky top-0 z-40 border-b border-border/80 bg-background/90 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
        <div className="flex items-center gap-10">
          <Link href="/">
            <JivanaLogo size="sm" />
          </Link>
          <nav className="hidden items-center gap-6 text-sm text-muted-foreground sm:flex">
            <Link href="/dashboard" className="font-medium text-foreground">
              Workspace
            </Link>
            <Link href="/dashboard#meetings">Meetings</Link>
            <Link href="/">About JIVANA</Link>
          </nav>
        </div>
        <div className="flex items-center gap-2">
          <LoginButton />
          <DropdownMenu>
            <DropdownMenuTrigger className="relative size-9 rounded-full outline-none focus-visible:ring-2 focus-visible:ring-ring">
              <Avatar className="size-9">
                <AvatarFallback>{initials}</AvatarFallback>
              </Avatar>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuLabel>{user?.email ?? "Guest user"}</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem disabled>Profile</DropdownMenuItem>
              <DropdownMenuItem disabled>Preferences</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}
