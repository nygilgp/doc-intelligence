# Requirements — Document Intelligence & Support Application

## Business requirement
Let customers self-serve on their documents so support ticket volume drops.

## Functional requirements
- Accept uploads: PDF (document block) and images (vision).
- Answer questions grounded ONLY in the provided document; say "I don't know" otherwise.
- Extract structured fields (e.g., invoice: vendor, total, due_date) as JSON.
- Hold bounded multi-turn support sessions.
- Escalate to a human when confidence is low.

## Infrastructure requirements
- Compute: AWS Lambda.        Storage: S3 (documents), DynamoDB (session state).
- Secrets: AWS Secrets Manager (S6).   Vendor: Anthropic API or Bedrock (ADR, E13).
- Expected volume: ~10k docs/day.   Latency target: < 5s interactive; bulk → Batch.
- Budget: track tokens/cost (usage logging, S2).

## Life cycle note
Ship is not done: operate & maintain — monitor cost/latency, manage model version
pinning (E22 / S2 E11), review dependency updates.