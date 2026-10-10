from html import escape

from app.schemas.meddocs import MedReconciliationJob


def render_review_summary_html(job: MedReconciliationJob) -> str:
    rows = []
    for item in job.discrepancy_items:
        detected = ""
        if item.discrepancy:
            detected = f"{item.discrepancy.discrepancy_type.value}: {item.discrepancy.summary}"
        elif item.finding:
            detected = f"{item.finding.code}: {item.finding.message}"
        latest = item.review.note if item.review else "—"
        rows.append(
            f"<tr><td>{escape(detected)}</td>"
            f"<td>{escape(item.status.value)}</td>"
            f"<td>{escape(latest)}</td></tr>"
        )
        for ev in item.review_history:
            rows.append(
                f"<tr class='hist'><td colspan='2'>"
                f"{escape(ev.from_status.value)} → {escape(ev.to_status.value)} "
                f"({escape(ev.reviewed_at)})</td>"
                f"<td>{escape(ev.note)}</td></tr>"
            )

    legacy = ""
    if job.legacy_bulk_review:
        legacy = (
            f"<p><strong>Legacy bulk acknowledgement</strong> "
            f"{escape(job.legacy_bulk_review.reviewed_at)}: "
            f"{escape(job.legacy_bulk_review.note or '')}</p>"
        )

    finalized = ""
    if job.finalized_at:
        finalized = (
            f"<p><strong>Current finalization</strong> {escape(job.finalized_at)} by "
            f"{escape(job.finalized_by_display or '')}</p>"
        )

    superseded_rows = []
    for rec in job.finalization_history:
        if rec.superseded_at:
            superseded_rows.append(
                "<tr>"
                f"<td>{escape(rec.finalized_at)}</td>"
                f"<td>{escape(rec.finalized_by_display or '—')}</td>"
                f"<td>{escape(rec.superseded_at)}</td>"
                f"<td>{escape(rec.superseded_reason or '')}</td>"
                "</tr>"
            )
    superseded_block = ""
    if superseded_rows:
        superseded_block = (
            "<h2>Prior finalizations (superseded)</h2>"
            "<table><thead><tr>"
            "<th>Finalized at</th><th>Reviewer</th><th>Superseded at</th><th>Reason</th>"
            "</tr></thead><tbody>"
            f"{''.join(superseded_rows)}</tbody></table>"
        )

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"/>
<title>Review summary — {escape(job.case_label or job.job_id)}</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2rem; }}
.banner {{ background: #f1f5f9; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #e2e8f0; padding: 8px; text-align: left; }}
tr.hist td {{ font-size: 0.85rem; color: #475569; }}
</style></head><body>
<div class="banner">Synthetic demo — not clinical approval. Review documentation only.</div>
<h1>{escape(job.case_label or "Medication transition case")}</h1>
<p>MRN: {escape(job.synthetic_mrn or "—")} · Transition: {escape(job.transition_type)}</p>
{legacy}{finalized}
{superseded_block}
<h2>Items</h2>
<table><thead><tr><th>Detected</th><th>Status</th><th>Latest note</th></tr></thead>
<tbody>{"".join(rows) if rows else "<tr><td colspan='3'>No items</td></tr>"}</tbody></table>
</body></html>"""
