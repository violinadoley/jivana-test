import { cn } from "@/lib/utils";

type Props = {
  className?: string;
  size?: number;
};

/** Simple mark — paired loops suggesting continuity of care. */
export function JivanaMark({ className, size = 28 }: Props) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={cn("shrink-0", className)}
      aria-hidden
    >
      <rect width="32" height="32" rx="10" className="fill-primary/10" />
      <path
        d="M11 16c0-2.2 1.8-4 4-4s4 1.8 4 4-1.8 4-4 4"
        className="stroke-primary"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <path
        d="M21 16c0-2.2 1.8-4 4-4"
        className="stroke-primary/70"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <circle cx="15" cy="16" r="1.5" className="fill-primary" />
    </svg>
  );
}
