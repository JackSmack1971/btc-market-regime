# Forensic Schema Validation Pattern

## Context
Use this pattern in QA suites to detect "silent drift" in external API responses that could break parsing logic without causing a direct 4xx/5xx error.

## Problem
APIs often change their JSON structure (changing a key, nesting a field, or changing a data type) without incrementing their version. Defensive parsing helps, but a dedicated validation layer is needed for certification.

## Solution
Perform "Forensic Probes" that verify not just the presence of data, but the existence and type of all mandatory keys required by the implementation.

### Structural Skeleton
```python
def check_forensic_schema(data):
    # Requirement: Must be a dict, have a 'data' array, 
    # and first item must have 'value' (float) and 'timestamp' (str)
    return (
        isinstance(data, dict) and 
        isinstance(data.get('data'), list) and 
        len(data['data']) > 0 and 
        all(k in data['data'][0] for k in ["value", "timestamp"]) and
        isinstance(data['data'][0]['value'], (float, int, str))
    )
```

## Gotchas
- **429 Noise**: Forensic probes often hit APIs rapidly. Always implement a retry loop with exponential backoff specifically for the validation suite.
- **Deep Key Mapping**: Don't just check `if "key" in data`. Verify recursive structures for nested metrics.
