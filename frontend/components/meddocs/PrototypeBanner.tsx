import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

export function PrototypeBanner() {
  return (
    <Alert variant="default" className="border-amber-500/40 bg-amber-500/5">
      <AlertTitle>MedDocs prototype (Module 1)</AlertTitle>
      <AlertDescription>
        Synthetic documents only. Not clinically validated. Human review is
        required for all medication discrepancies — no regimen approval actions.
      </AlertDescription>
    </Alert>
  );
}
