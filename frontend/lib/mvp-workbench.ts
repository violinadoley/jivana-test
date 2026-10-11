/**
 * Canonical JIVANA UI (default): discharge med rec workbench + enterprise tool tabs.
 * `NEXT_PUBLIC_MVP_WORKBENCH=false` enables a **deprecated** legacy eight-tab sandbox
 * (one-shot Documents queue). Production builds use `true`. Removal planned in a future release.
 */
export const mvpWorkbenchEnabled =
  process.env.NEXT_PUBLIC_MVP_WORKBENCH !== "false";
