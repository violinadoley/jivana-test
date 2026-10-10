/**
 * Hybrid workspace (default): discharge med rec + Search/Copilot/Meetings/etc.
 * Set NEXT_PUBLIC_MVP_WORKBENCH=false for the legacy eight-tab engineer sandbox.
 */
export const mvpWorkbenchEnabled =
  process.env.NEXT_PUBLIC_MVP_WORKBENCH !== "false";
