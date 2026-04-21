# CodeCleanup Sample

Run `/CodeCleanup` on this file to see the workflow in action.

## Before: Code with cleanup opportunities

```python
# --- data_service.py ---
# This file handles fetching and processing data from multiple sources.

import json
import os

SOURCES = {"api": APISource, "file": FileSource, "db": DBSource}

# get data from api and parse it
def get(source, id):
    s = SOURCES.get(source)
    if s:
        raw = s.fetch(id)
        if raw:
            # parse the response
            data = json.loads(raw)
            result = data["items"][0]  # get first item
            if result.get("status") == "active":
                name = result["name"]
                tags = result.get("tags", [])
                processed = {"name": name, "tags": tags, "source": source}
                # validate
                if not name:
                    print("Error")
                    return None
                # also check tags
                for t in tags:
                    if not isinstance(t, str):
                        print("Error")
                        return None
                return processed
            else:
                return None
        else:
            return None
    else:
        return None

# same thing but for batch
def get_batch(source, ids):
    results = []
    for id in ids:
        s = SOURCES.get(source)
        if s:
            raw = s.fetch(id)
            if raw:
                data = json.loads(raw)
                result = data["items"][0]
                if result.get("status") == "active":
                    name = result["name"]
                    tags = result.get("tags", [])
                    processed = {"name": name, "tags": tags, "source": source}
                    if name and all(isinstance(t, str) for t in tags):
                        results.append(processed)
    return results

# load config
def cfg():
    with open("config.json") as f:
        return json.load(f)
```

## Cleanup Findings

| # | Category | Finding |
|---|----------|---------|
| 1 | Naming | `get()` is ambiguous — rename to `fetch_active_item()` |
| 2 | Naming | `cfg()` is cryptic — rename to `load_config()` |
| 3 | Naming | `s`, `t`, `id` are single-letter — use `source_client`, `tag`, `item_id` |
| 4 | Duplication | `get()` and `get_batch()` share identical parse+validate logic |
| 5 | Readability | `get()` has 6 levels of nesting — flatten with guard clauses |
| 6 | Defense | `data["items"][0]` indexes without emptiness check |
| 7 | Defense | `print("Error")` gives no context — make actionable |
| 8 | Decomposition | Parse, validate, and fetch all in one function — extract helpers |

## After: Cleaned up

```python
# --- data_service.py ---

import json

SOURCES = {"api": APISource, "file": FileSource, "db": DBSource}


def fetch_active_item(source_name, item_id):
    source_client = SOURCES.get(source_name)
    if not source_client:
        return None

    raw = source_client.fetch(item_id)
    if not raw:
        return None

    item = parse_first_active_item(raw, source_name)
    if item and validate_item(item):
        return item
    return None


def fetch_active_items_batch(source_name, item_ids):
    source_client = SOURCES.get(source_name)
    if not source_client:
        return []

    results = []
    for item_id in item_ids:
        raw = source_client.fetch(item_id)
        if not raw:
            continue
        item = parse_first_active_item(raw, source_name)
        if item and validate_item(item):
            results.append(item)
    return results


def parse_first_active_item(raw_response, source_name):
    data = json.loads(raw_response)
    if not data.get("items"):
        return None

    first_item = data["items"][0]
    if first_item.get("status") != "active":
        return None

    return {
        "name": first_item["name"],
        "tags": first_item.get("tags", []),
        "source": source_name,
    }


def validate_item(item):
    if not item.get("name"):
        raise ValueError(f"Item missing name (source: {item['source']})")

    invalid_tags = [t for t in item.get("tags", []) if not isinstance(t, str)]
    if invalid_tags:
        raise ValueError(
            f"Item '{item['name']}' has non-string tags: {invalid_tags}"
        )

    return True


def load_config(path="config.json"):
    with open(path) as config_file:
        return json.load(config_file)
```
