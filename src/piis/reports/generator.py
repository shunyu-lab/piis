from pathlib import Path

from piis.models.enums import ClaimType, RelationLabel
from piis.models.report import Report

_TYPE_NOTE = {
    ClaimType.FACT: "Presented as fact by the source — not verified by PIIS.",
    ClaimType.OPINION: "Opinion.",
    ClaimType.PREDICTION: "Prediction — not a current fact.",
    ClaimType.INTERPRETATION: "Interpretation.",
    ClaimType.VALUE_JUDGMENT: "Value judgment.",
    ClaimType.QUESTION: "Question.",
    ClaimType.UNKNOWN: "Unclassified.",
}


class ReportGenerator:
    def __init__(self, output_dir: Path) -> None:
        self._output_dir = output_dir
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def write(self, report: Report) -> Report:
        markdown_path = self._output_dir / f"{report.id}.md"
        json_path = self._output_dir / f"{report.id}.json"
        markdown_path.write_text(render_markdown(report), encoding="utf-8")
        json_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
        return report.model_copy(
            update={"markdown_path": str(markdown_path), "json_path": str(json_path)}
        )


def render_markdown(report: Report) -> str:
    content = report.content
    lines = [
        "# Information Analysis Report",
        "",
        "## Content",
        "",
        f"Title: {content.title}",
        f"Author: {content.author or 'unknown'}",
        f"Source: {content.source_url}",
        f"Source type: {content.source_type.value}",
        "",
        "## Summary",
        "",
        (
            f"{len(report.claims)} claims compared with domain, primary, and personal knowledge. "
            "Scores describe relations, not truth."
        ),
        "",
        f"- Novelty (aggregate): {report.diff.novelty_score:.2f}",
        f"- Supporting: {report.diff.supporting_score:.2f}",
        f"- Conflict: {report.diff.conflict_score:.2f}",
        f"- Redundancy: {report.diff.redundancy_score:.2f}",
        f"- Evidence gap: {report.diff.evidence_gap_score:.2f}",
        f"- Engine: `{report.diff.engine}` (method: {report.diff.method.value})",
        "",
        "## Claims",
        "",
    ]
    for index, claim in enumerate(report.claims, start=1):
        lines.extend(
            [
                f"### Claim {index}",
                "",
                f"Type: {claim.claim_type.value} (framing, not verification)",
                f"Framing: {_TYPE_NOTE[claim.claim_type]}",
                "Verification: UNVERIFIED",
                f"Confidence (extractor identification, not truth): {claim.confidence:.2f}",
                "",
                "Content:",
                "",
                claim.content,
                "",
            ]
        )
        if claim.evidence:
            lines.append("Evidence spans:")
            lines.extend(f"- {span.text}" for span in claim.evidence)
            lines.append("")
        else:
            lines.append("Evidence spans: none attached.")
            lines.append("")

    lines.extend(_section("Novel Information", report, RelationLabel.UNRELATED))
    lines.extend(_section("Related Information", report, RelationLabel.RELATED, RelationLabel.SUPPORTING))
    lines.extend(_section("Potential Conflicts", report, RelationLabel.CONFLICTING))
    lines.extend(_section("Redundant Information", report, RelationLabel.REDUNDANT))

    lines.extend(["## Evidence Gaps", ""])
    if report.evidence.claim_gaps:
        for claim_id, note in report.evidence.claim_gaps.items():
            statement = next(c.content for c in report.claims if c.id == claim_id)
            lines.append(f"- {statement}")
            lines.append(f"  - {note}")
        lines.append("")
    else:
        lines.append("No extractor-level evidence gaps flagged.")
        lines.append("")
    for note in report.evidence.notes:
        lines.append(f"- {note}")
    lines.extend(["", "## Relation To Personal Knowledge", ""])

    personal_bits = [
        rel
        for analysis in report.diff.claim_analyses
        for rel in analysis.relations
        if rel.store.value == "personal" and rel.label is not RelationLabel.UNRELATED
    ]
    if not personal_bits:
        lines.append("No personal-knowledge relations in this run.")
        lines.append("")
    else:
        lines.append("Personal beliefs are cognitive state, not facts. PIIS will not change them.")
        lines.append("")
        for rel in personal_bits:
            analysis = next(a for a in report.diff.claim_analyses if a.claim_id == rel.claim_id)
            lines.append(f"- Your knowledge item `{rel.knowledge_id}` vs claim:")
            lines.append(f"  {analysis.statement}")
            lines.append(f"  Relation: **{rel.label.value}** — {rel.rationale}")
            if rel.label == RelationLabel.CONFLICTING:
                lines.append("  Suggested re-evaluation only. Belief left unchanged.")
            lines.append("")

    lines.extend(["## Suggested Follow-up", ""])
    lines.extend(f"- {item}" for item in report.follow_ups)
    lines.extend(
        [
            "",
            "## Limitations",
            "",
            "- V0.1 uses mock providers and a heuristic relation classifier.",
            "- Embedding similarity is a retrieval/feature signal, not a verdict.",
            "- Controversial domains must not treat model output as objective fact.",
            "",
        ]
    )
    return "\n".join(lines)


def _section(title: str, report: Report, *labels: RelationLabel) -> list[str]:
    lines = [f"## {title}", ""]
    matched = [a for a in report.diff.claim_analyses if a.primary_label in labels]
    if not matched:
        lines.append("None in this run.")
        lines.append("")
        return lines
    for analysis in matched:
        lines.append(f"- ({analysis.claim_type.value}) {analysis.statement}")
        lines.append(f"  - {analysis.notes}")
    lines.append("")
    return lines
