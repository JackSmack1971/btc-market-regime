# ALERTING STRATEGIES & PATTERNS

## 1. Stateful Transition Detection (Pattern #8)
**Context**: Preventing notification "storms" during rapid price fluctuations or repetitive data refreshes.
**Implementation**:
- Utilize the `db_manager.cache` (SQLite) to store the `last_known_state`.
- Trigger the notification logic **only** if `current_state != last_known_state`.
- Update the cache **immediately after** successful dispatch.

## 2. Async Notifier Contract (Pattern #9)
**Context**: Ensuring that alerting logic does not block the primary analytical pipeline (CLI/Dashboard).
**Implementation**:
- Define a base `Notifier` ABC with an `async def send()` contract.
- Use `aiohttp.ClientSession` for non-blocking HTTP POSTs to third-party APIs (Telegram, Slack, etc.).
- Implement "Fail-Silent" architecture: Log failures to STDERR/logger but return `False` to prevent application crashes.

## 3. Environment-Driven Credentialing
- Protect sensitive keys (Tokens, Chat IDs) using `.env` files and `python-dotenv`.
- Use `os.getenv()` with fallback/validation to ensure specific notifications only fire when credentials are present.
