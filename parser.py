# import json
# import re
# from collections import Counter
# import math
# from urllib.parse import urlparse

# # ---------- SAFE HELPERS ---------- #
# def safe_div(a, b):
#     return a / b if b != 0 else 0

# def variance(lst):
#     if not lst:
#         return 0
#     mean = sum(lst) / len(lst)
#     return sum((x - mean) ** 2 for x in lst) / len(lst)

# def entropy(lst):
#     if not lst:
#         return 0
#     c = Counter(lst)
#     total = len(lst)
#     return -sum((v / total) * math.log2(v / total) for v in c.values())

# # ---------- DATA COLLECTION ---------- #
# data = {
#     "urls": [],
#     "files": [],
#     "activities": [],
#     "device_access": 0,
#     "crypto": 0,
#     "sp": []
# }

# with open("output.txt", "r", encoding="utf-8", errors="ignore") as f:
#     for line in f:
#         line = re.sub(r'[^\x20-\x7E]+', '', line)

#         if "[URL]" in line:
#             data["urls"].append(line.split("[URL]")[-1].strip())

#         elif "[File]" in line:
#             data["files"].append(line.split("[File]")[-1].strip())

#         elif "[Activity]" in line:
#             data["activities"].append(line.split("[Activity]")[-1].strip())

#         elif "[DeviceID Access]" in line:
#             data["device_access"] += 1

#         elif "[Crypto]" in line:
#             data["crypto"] += 1

#         elif "[SP]" in line:
#             data["sp"].append(line.split("[SP]")[-1].strip())

# # ---------- FEATURE ENGINEERING ---------- #
# features = {}

# urls = data["urls"]
# files = data["files"]
# acts = data["activities"]

# # ---------- NETWORK ---------- #
# domains, paths, query_counts = [], [], []

# for u in urls:
#     try:
#         parsed = urlparse(u)
#         domains.append(parsed.netloc)
#         paths.append(parsed.path)
#         query_counts.append(len(parsed.query.split("&")) if parsed.query else 0)
#     except:
#         continue

# domain_counts = Counter(domains)
# tlds = [d.split(".")[-1] for d in domains if "." in d]

# # Basic
# features["unique_domains"] = len(domain_counts)
# features["total_requests"] = len(urls)
# features["avg_requests_per_domain"] = safe_div(len(urls), len(domain_counts))

# # Domain categories
# keywords = ["facebook","google","amazon","microsoft","cloud","api","cdn","ads","track"]
# for k in keywords:
#     features[f"domain_{k}_count"] = sum(1 for d in domains if k in d)

# # TLD
# for t in ["com","net","org","ru","cn","info"]:
#     features[f"tld_{t}"] = tlds.count(t)

# # Suspicious
# features["non_https"] = sum(1 for u in urls if u.startswith("http://"))
# features["ip_based_urls"] = sum(1 for d in domains if re.match(r"\d+\.\d+\.\d+\.\d+", d))
# features["long_url_count"] = sum(1 for u in urls if len(u) > 100)

# # Frequency
# features["high_freq_domains"] = sum(1 for c in domain_counts.values() if c > 10)
# features["medium_freq_domains"] = sum(1 for c in domain_counts.values() if 3 <= c <= 10)
# features["low_freq_domains"] = sum(1 for c in domain_counts.values() if c < 3)

# # URL stats
# url_lengths = [len(u) for u in urls]
# features["avg_url_length"] = safe_div(sum(url_lengths), len(url_lengths))
# features["max_url_length"] = max(url_lengths) if url_lengths else 0
# features["min_url_length"] = min(url_lengths) if url_lengths else 0

# features["avg_query_params"] = safe_div(sum(query_counts), len(query_counts))
# features["max_query_params"] = max(query_counts) if query_counts else 0

# # ---------- FILE ---------- #
# features["file_access_count"] = len(files)
# features["unique_file_paths"] = len(set(files))

# patterns = {
#     "shared_prefs": "shared_prefs",
#     "system": "/system",
#     "data": "/data",
#     "cache": "cache",
#     "db": ".db",
#     "log": "log",
#     "tmp": "tmp",
#     "keychain": "keychain"
# }

# for k, v in patterns.items():
#     features[f"file_{k}_count"] = sum(1 for f in files if v in f)

# depths = [len(f.split("/")) for f in files if "/" in f]
# features["avg_file_depth"] = safe_div(sum(depths), len(depths))
# features["max_file_depth"] = max(depths) if depths else 0

# # ---------- ACTIVITY ---------- #
# features["num_activities"] = len(set(acts))
# features["activity_total"] = len(acts)

# for k in ["login","main","splash","ads","web","register"]:
#     features[f"activity_{k}"] = sum(1 for a in acts if k in a.lower())

# features["activity_transitions"] = len(acts)

# # ---------- API ---------- #
# features["device_id_access"] = data["device_access"]
# features["crypto_usage"] = data["crypto"]
# features["sp_access_count"] = len(data["sp"])
# features["unique_sp_keys"] = len(set(data["sp"]))

# # ---------- STATISTICS ---------- #
# features["domain_entropy"] = entropy(domains)
# features["file_entropy"] = entropy(files)
# features["activity_entropy"] = entropy(acts)

# features["url_length_variance"] = variance(url_lengths)
# features["file_depth_variance"] = variance(depths)

# # ---------- EXTRA FEATURES ---------- #
# domain_values = list(domain_counts.values())

# features["max_domain_hits"] = max(domain_values) if domain_values else 0
# features["min_domain_hits"] = min(domain_values) if domain_values else 0
# features["domain_variance"] = variance(domain_values)

# total_hits = sum(domain_values)
# for i, (dom, cnt) in enumerate(domain_counts.most_common(5)):
#     features[f"top_domain_{i}_ratio"] = safe_div(cnt, total_hits)

# url_depths = [len(u.split("/")) for u in urls if "/" in u]
# features["avg_url_depth"] = safe_div(sum(url_depths), len(url_depths))
# features["max_url_depth"] = max(url_depths) if url_depths else 0

# features["url_has_query"] = sum(1 for u in urls if "?" in u)
# features["url_has_params"] = sum(1 for u in urls if "&" in u)
# features["url_has_equals"] = sum(1 for u in urls if "=" in u)

# features["suspicious_tld_ratio"] = safe_div(
#     sum(1 for t in tlds if t in ["ru","cn","info"]), len(tlds)
# )

# # File extensions
# exts = [f.split(".")[-1] for f in files if "." in f]
# ext_counts = Counter(exts)

# for ext in ["xml","db","txt","log","json","tmp"]:
#     features[f"file_ext_{ext}"] = ext_counts.get(ext, 0)

# features["repeated_file_access"] = sum(1 for c in Counter(files).values() if c > 1)

# features["system_access_ratio"] = safe_div(sum(1 for f in files if "/system" in f), len(files))
# features["data_access_ratio"] = safe_div(sum(1 for f in files if "/data" in f), len(files))

# # Activity
# act_counts = Counter(acts)
# features["repeated_activity"] = sum(1 for c in act_counts.values() if c > 1)
# features["unique_activity_ratio"] = safe_div(len(set(acts)), len(acts))

# transitions = [(acts[i], acts[i+1]) for i in range(len(acts)-1)]
# features["unique_transitions"] = len(set(transitions))

# # API flags
# features["uses_crypto_flag"] = int(data["crypto"] > 0)
# features["device_access_flag"] = int(data["device_access"] > 0)
# features["sp_diversity_ratio"] = safe_div(len(set(data["sp"])), len(data["sp"]))

# # Stats
# features["url_length_std"] = math.sqrt(variance(url_lengths)) if url_lengths else 0

# file_lengths = [len(f) for f in files]
# features["avg_file_length"] = safe_div(sum(file_lengths), len(file_lengths))
# features["file_length_variance"] = variance(file_lengths)

# features["activity_variance"] = variance([len(a) for a in acts]) if acts else 0

# total_events = len(urls) + len(files) + len(acts)
# features["event_density"] = total_events
# features["url_ratio"] = safe_div(len(urls), total_events)
# features["file_ratio"] = safe_div(len(files), total_events)
# features["activity_ratio"] = safe_div(len(acts), total_events)

# features["network_to_file_ratio"] = safe_div(len(urls), len(files))
# features["network_to_activity_ratio"] = safe_div(len(urls), len(acts))
# features["file_to_activity_ratio"] = safe_div(len(files), len(acts))

# features["combined_entropy"] = entropy(domains + files + acts)

# # ---------- SAVE ---------- #
# with open("output.json", "w") as f:
#     json.dump(features, f, indent=4)

# print(f"🔥 TOTAL FEATURES: {len(features)}")
# print("✅ Feature extraction complete")


import json

events = []

with open("output.txt", "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        line = line.strip()

        try:
            obj = json.loads(line)
            events.append(obj)
        except:
            continue

with open("output.json", "w") as f:
    json.dump(events, f, indent=2)

print(f"✅ Raw events captured: {len(events)}")