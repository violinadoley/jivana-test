import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

export function PrototypeBanner() {
  return (
    <Alert variant="default" className="border-primary/20 bg-primary/5">
      <AlertTitle>For training and demonstration</AlertTitle>
      <AlertDescription>
        Use sample or de-identified documents only. JIVANA highlights differences between
        medication lists—it does not approve orders or replace your clinical judgment. Every
        flagged item needs a documented decision by a licensed clinician or pharmacist.
      </AlertDescription>
    </Alert>
  );
}
