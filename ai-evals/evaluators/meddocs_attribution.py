"""Compare resolved source refs to expected block ids (offline gold in case fixtures)."""


def attribution_matches(
    resolved_block_ids: list[str],
    gold_block_ids: list[str],
) -> bool:
    if not gold_block_ids:
        return True
    return set(gold_block_ids).issubset(set(resolved_block_ids))
