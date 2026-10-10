import Image from "next/image";
import Link from "next/link";
import { ArrowRight01Icon } from "@hugeicons/core-free-icons";

import { HugeIcon } from "@/components/ui/huge-icon";

const audiences = [
  {
    title: "Healthcare professionals",
    body: "Compare discharge med lists, resolve each difference with a note, and sign off when the chart is ready.",
    image: "/images/audience-pharmacy.jpg",
    href: "/dashboard",
  },
  {
    title: "Clinical operations",
    body: "Quality and ops leaders get visibility into open reviews, completed sign-offs, and items waiting on external follow-up.",
    image: "/images/audience-ops.jpg",
    href: "/#product",
  },
] as const;

export function HomeAudienceSection() {
  return (
    <section className="bg-background py-20 sm:py-24">
      <div className="mx-auto grid max-w-6xl gap-6 px-4 sm:grid-cols-2 sm:px-6">
        {audiences.map((item) => (
          <article
            key={item.title}
            className="overflow-hidden rounded-3xl border border-border/60 bg-card shadow-[0_8px_40px_-16px_rgba(15,23,42,0.12)]"
          >
            <div className="relative h-44 w-full">
              <Image
                src={item.image}
                alt=""
                fill
                className="object-cover"
                sizes="(max-width: 640px) 100vw, 50vw"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-card via-card/20 to-transparent" />
            </div>
            <div className="p-8 pt-4">
              <h3 className="text-xl font-semibold text-foreground">{item.title}</h3>
              <p className="mt-3 text-sm leading-relaxed text-muted-foreground">{item.body}</p>
              <Link
                href={item.href}
                className="mt-6 inline-flex items-center gap-1.5 text-sm font-medium text-primary"
              >
                Learn more
                <HugeIcon icon={ArrowRight01Icon} size={16} />
              </Link>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
