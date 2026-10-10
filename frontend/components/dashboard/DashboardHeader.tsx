"use client";

import Link from "next/link";

import { LoginButton } from "@/components/auth/LoginButton";
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
    <header className="sticky top-0 z-40 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4 sm:px-6">
        <div className="flex items-center gap-6">
          <Link href="/" className="font-semibold tracking-tight">
            PROJECT_NAME
          </Link>
          <nav className="hidden sm:flex items-center gap-4 text-sm text-muted-foreground">
            <Link href="/dashboard" className="text-foreground font-medium">
              Dashboard
            </Link>
            <Link
              href="/dashboard#recent-activity"
              className="hover:text-foreground"
            >
              Activity
            </Link>
          </nav>
        </div>
        <div className="flex items-center gap-2">
          <LoginButton />
          <DropdownMenu>
            <DropdownMenuTrigger
              className="relative size-9 rounded-full outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              <Avatar className="size-9">
                <AvatarFallback>{initials}</AvatarFallback>
              </Avatar>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuLabel>
                {user?.email ?? "Guest user"}
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem disabled>Profile (competition build)</DropdownMenuItem>
              <DropdownMenuItem disabled>Preferences (competition build)</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}
