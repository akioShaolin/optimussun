import hashlib
import json


PLAN_HASH_FIELDS = (
    "format_version", "mapping_version", "source", "decisions_sha256",
    "counts", "tables", "mappings", "issues",
)


def plan_sha256(plan):
    """Return the canonical checksum of every import-plan payload field."""
    payload = {field: plan[field] for field in PLAN_HASH_FIELDS}
    source = payload["source"]
    payload["source"] = {
        key: source[key]
        for key in ("source_id", "source_sha256", "snapshot_sha256")
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True,
                           separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
