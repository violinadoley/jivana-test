import Image from "next/image";

import { cn } from "@/lib/utils";

type Props = {
  className?: string;
};

/**
 * Hero photo from /public — never depends on Unsplash at runtime.
 */
export function HeroVisual({ className }: Props) {
  return (
    <div
      className={cn(
        "hero-blob relative aspect-[4/5] overflow-hidden bg-gradient-to-br from-primary/20 via-accent to-primary/5",
        "shadow-[0_32px_64px_-24px_rgba(15,23,42,0.25)]",
        className
      )}
    >
      <Image
        src="/images/hero-clinician.jpg"
        alt="Healthcare professional in clinical setting"
        fill
        className="object-cover"
        priority
        sizes="(max-width: 1024px) 90vw, 480px"
      />
    </div>
  );
}
