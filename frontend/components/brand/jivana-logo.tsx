import { JivanaMark } from "@/components/brand/jivana-mark";
import { cn } from "@/lib/utils";

type Props = {
  className?: string;
  size?: "sm" | "md" | "lg" | "hero";
  showTagline?: boolean;
  inverted?: boolean;
};

const wordmarkSize = {
  sm: "text-lg leading-none",
  md: "text-xl leading-none",
  lg: "text-2xl leading-none",
  hero: "text-3xl sm:text-4xl leading-none",
} as const;

const markSize = {
  sm: 26,
  md: 30,
  lg: 36,
  hero: 40,
} as const;

export function JivanaLogo({
  className,
  size = "md",
  showTagline = false,
  inverted = false,
}: Props) {
  return (
    <span className={cn("inline-flex items-center gap-2.5", className)}>
      <JivanaMark size={markSize[size]} />
      <span className="inline-flex flex-col">
        <span
          className={cn(
            "font-semibold tracking-tight",
            wordmarkSize[size],
            inverted ? "text-white" : "text-foreground"
          )}
          aria-label="Jivana"
        >
          Jivana
        </span>
        {showTagline ? (
          <span
            className={cn(
              "mt-0.5 text-[0.65rem] font-medium uppercase tracking-[0.18em]",
              inverted ? "text-white/70" : "text-muted-foreground"
            )}
          >
            Healthcare intelligence
          </span>
        ) : null}
      </span>
    </span>
  );
}
