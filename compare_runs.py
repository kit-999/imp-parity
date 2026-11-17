#!/usr/bin/env python3
"""Compare two golden-trace runs case by case and sort the 42 cases into categories.

  python3 compare_runs.py runs/golden-331.json runs/golden-350.json path/to/imp/test/fixtures/golden_trace/cases.json
Compares every recorded field: status, prediction, tool trace, error, and each LM call's messages and kwargs."""
import json, sys
from collections import OrderedDict

a_path, b_path, cases_path = sys.argv[1:4]
cases = {c["id"]: c for c in json.load(open(cases_path))}
a = {c["id"]: c for c in json.load(open(a_path))["cases"]}
b = {c["id"]: c for c in json.load(open(b_path))["cases"]}
cats = OrderedDict()
for i in a:
    x, y = a[i], b[i]
    msgs = lambda r: [json.dumps(e.get("messages"), sort_keys=True) for e in r["history"]]
    kw = lambda r: [e.get("kwargs") for e in r["history"]]
    m, k = msgs(x) == msgs(y), kw(x) == kw(y)
    p, s, t, e = x["prediction"] == y["prediction"], x["status"] == y["status"], x["tool_trace"] == y["tool_trace"], x["error"] == y["error"]
    if all((m, k, p, s, t, e)):
        c = "identical in every recorded field"
    elif x["status"] == "ok" and y["status"] == "error":
        c = "ran on the first, fails on the second (prompt changed)"
    elif m and p and s and not k:
        c = "same prompt and prediction, request options moved"
    elif s and p and not m:
        c = "prompt changed, same prediction"
    elif x["status"] == "error" and y["status"] == "error":
        c = "designed error case, error text or prompt changed"
    else:
        c = "other"
    cats.setdefault(c, []).append(f"{i} ({cases[i]['module']}/{cases[i].get('adapter') or 'chat'})")
for c, ids in cats.items():
    print(f"{len(ids):3d}  {c}")
    for z in ids:
        print("       ", z)
print("total", sum(len(v) for v in cats.values()))
