CONFIDENCE_PROMPT = """
You are scoring response reliability.
Return only JSON with keys:
- confidence: float between 0 and 1
- risk: low|medium|high
- reason: short string

Consider:
- evidence quality
- directness of answer to query
- policy/legal sensitivity
""".strip()
