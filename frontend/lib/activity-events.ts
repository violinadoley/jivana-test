export const ACTIVITY_UPDATED_EVENT = "hackathon-activity-updated";

export function notifyActivityUpdated(): void {
  if (typeof window !== "undefined") {
    window.dispatchEvent(new Event(ACTIVITY_UPDATED_EVENT));
  }
}
