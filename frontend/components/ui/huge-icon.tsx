import { HugeiconsIcon } from "@hugeicons/react";
import type { ComponentProps } from "react";

type IconData = ComponentProps<typeof HugeiconsIcon>["icon"];

export function HugeIcon({
  icon,
  size = 22,
  className,
  strokeWidth = 1.75,
}: {
  icon: IconData;
  size?: number;
  className?: string;
  strokeWidth?: number;
}) {
  return (
    <HugeiconsIcon
      icon={icon}
      size={size}
      strokeWidth={strokeWidth}
      color="currentColor"
      className={className}
    />
  );
}
