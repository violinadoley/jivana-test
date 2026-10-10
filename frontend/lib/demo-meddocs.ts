const DEMO_FILES = [
  { path: "/demo-meddocs/prior_sample.txt", name: "prior_sample.txt" },
  { path: "/demo-meddocs/discharge_sample.txt", name: "discharge_sample.txt" },
  { path: "/demo-meddocs/rx_sample.txt", name: "rx_sample.txt" },
] as const;

export async function loadSyntheticDemoMeddocs(): Promise<File[]> {
  const files: File[] = [];
  for (const spec of DEMO_FILES) {
    const response = await fetch(spec.path);
    if (!response.ok) {
      throw new Error(`Could not load demo file ${spec.name}.`);
    }
    const blob = await response.blob();
    files.push(new File([blob], spec.name, { type: "text/plain" }));
  }
  return files;
}
