import Link from "next/link";

import { HomeApproach } from "@/components/home/home-approach";
import { HomeAudienceSection } from "@/components/home/home-audience-section";
import { HomeClinicianBand } from "@/components/home/home-clinician-band";
import { HomeBottomCta } from "@/components/home/home-bottom-cta";
import { HomeFeatureRow } from "@/components/home/home-feature-row";
import { HomeHero } from "@/components/home/home-hero";
import { HomeProductShowcase } from "@/components/home/home-product-showcase";
import { HomeTrustStrip } from "@/components/home/home-trust-strip";
import { SiteFooter } from "@/components/layout/site-footer";
import { SiteHeader } from "@/components/layout/site-header";
import { brand, solutionPillars } from "@/lib/brand";

export default function HomePage() {
  return (
    <>
      <SiteHeader />
      <main className="flex-1">
        <HomeHero />
        <HomeFeatureRow />
        <HomeProductShowcase />
        <HomeTrustStrip />
        <HomeClinicianBand />
        <HomeAudienceSection />

        <section id="capabilities" className="section-soft py-20 sm:py-24">
          <div className="mx-auto max-w-6xl px-4 sm:px-6">
            <div className="mx-auto max-w-2xl text-center">
              <p className="eyebrow-accent">Capabilities</p>
              <h2 className="mt-3 text-3xl font-semibold tracking-tight text-foreground">
                Find, understand, and act—with proof
              </h2>
              <p className="mt-4 text-muted-foreground">{brand.problem}</p>
            </div>
            <ul className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {solutionPillars.map((pillar) => (
                <li
                  key={pillar.title}
                  className="rounded-3xl border border-border/60 bg-card p-8 shadow-[0_8px_32px_-16px_rgba(15,23,42,0.1)]"
                >
                  <h3 className="text-base font-semibold text-foreground">{pillar.title}</h3>
                  <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
                    {pillar.description}
                  </p>
                </li>
              ))}
            </ul>
            <div className="mt-12 text-center">
              <Link
                href="/dashboard"
                className="inline-flex h-11 items-center rounded-full bg-foreground px-6 text-sm font-medium text-background"
              >
                Open workspace
              </Link>
            </div>
          </div>
        </section>

        <HomeApproach />
        <HomeBottomCta />
      </main>
      <SiteFooter />
    </>
  );
}
