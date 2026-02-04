from marketmind_engine.policy.policy_result import PolicyResult


def format_policy_explanation(policy_result: PolicyResult) -> str:
    """
    Produce a human-readable explanation of a PolicyResult.
    """

    action = policy_result.action.value.upper()
    confidence_pct = int(policy_result.confidence * 100)

    lines = [
        f"Policy decision: {action} ({confidence_pct}% confidence)."
    ]

    if policy_result.triggered_rules:
        rules = ", ".join(policy_result.triggered_rules)
        lines.append(f"Triggered rules: {rules}.")
    else:
        lines.append("No decision rules were triggered.")

    if policy_result.gating_reasons:
        for reason in policy_result.gating_reasons:
            lines.append(f"Reason: {reason}.")

    return " ".join(lines)
