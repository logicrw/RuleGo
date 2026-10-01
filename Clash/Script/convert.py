#!/usr/bin/env python3
"""
Convert Surge / Clash classical rules to domain/ipcidr format for Clash/Mihomo.

Sources:
  - Local RuleGo Surge rules: AI, Gemini, Crypto rulesets (Surge list format)
  - blackmatrix7/ios_rule_script: per-service rulesets (classical format)

Output (in Clash/Ruleset/):
  - {name}.yaml       behavior: domain   (DOMAIN + DOMAIN-SUFFIX)
  - {name}-ip.yaml    behavior: ipcidr   (IP-CIDR + IP-CIDR6)
  - {name}-kw.yaml    behavior: classical (DOMAIN-KEYWORD only)

User-editable files (proxy-extra.yaml, direct-extra.yaml) are NOT overwritten.
"""

import os
import sys
import urllib.request

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RULES_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "Ruleset"))
LOCAL_SURGE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "Surge", "Ruleset"))

# --- Sources ---

BLACKMATRIX7 = "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash"
BM7_SERVICES = {
    "wechat":    "WeChat/WeChat.yaml",
    "bytedance": "ByteDance/ByteDance.yaml",
    "bilibili":  "BiliBili/BiliBili.yaml",
    "youtube":   "YouTube/YouTube.yaml",
    "netflix":   "Netflix/Netflix.yaml",
    "disney":    "Disney/Disney.yaml",
    "tiktok":    "TikTok/TikTok.yaml",
    "telegram":  "Telegram/Telegram.yaml",
    "twitter":   "Twitter/Twitter.yaml",
    "paypal":    "PayPal/PayPal.yaml",
    "apple":     "Apple/Apple_Classical.yaml",
    "google":    "Google/Google.yaml",
}

RULEGO_REMOTE = "https://raw.githubusercontent.com/logicrw/RuleGo/patch-1/Surge/Ruleset"
RULEGO_SERVICES = {
    "ai-extra": "Extra/AI.list",
    "gemini":   "Extra/GenAI/Google.list",
    "crypto":   "Extra/Crypto.list",
}


# --- Fetch ---

def get_content(url, local_path=None):
    if local_path and os.path.exists(local_path):
        try:
            with open(local_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"  WARN reading local {local_path}: {e}", file=sys.stderr)

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "rulego-converter"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8")
    except Exception as e:
        print(f"  WARN downloading {url}: {e}", file=sys.stderr)
        return None


# --- Parsers ---

def parse_classical(content):
    """Parse Clash classical payload."""
    r = {"domains": [], "suffixes": [], "keywords": [], "ipv4": [], "ipv6": []}
    in_payload = False
    for line in content.splitlines():
        s = line.strip()
        if s == "payload:":
            in_payload = True
            continue
        if not in_payload or not s.startswith("- "):
            continue
        rule = s[2:].strip().strip("'\"")
        if rule.startswith("DOMAIN-SUFFIX,"):
            r["suffixes"].append(rule.split(",", 1)[1])
        elif rule.startswith("DOMAIN-KEYWORD,"):
            r["keywords"].append(rule.split(",", 1)[1])
        elif rule.startswith("DOMAIN,"):
            r["domains"].append(rule.split(",", 1)[1])
        elif rule.startswith("IP-CIDR6,"):
            r["ipv6"].append(rule.split(",", 1)[1].split(",")[0])
        elif rule.startswith("IP-CIDR,"):
            r["ipv4"].append(rule.split(",", 1)[1].split(",")[0])
    return r


def parse_surge_list(content):
    """Parse Surge list format (one rule per line)."""
    r = {"domains": [], "suffixes": [], "keywords": [], "ipv4": [], "ipv6": []}
    for line in content.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        rule = s.split(",extended-matching")[0].strip()
        if rule.startswith("DOMAIN-SUFFIX,"):
            r["suffixes"].append(rule.split(",", 1)[1])
        elif rule.startswith("DOMAIN-KEYWORD,"):
            r["keywords"].append(rule.split(",", 1)[1])
        elif rule.startswith("DOMAIN,"):
            r["domains"].append(rule.split(",", 1)[1])
        elif rule.startswith("IP-CIDR6,"):
            r["ipv6"].append(rule.split(",", 1)[1].split(",")[0])
        elif rule.startswith("IP-CIDR,"):
            r["ipv4"].append(rule.split(",", 1)[1].split(",")[0])
    return r


# --- Writers ---

def write_domain(filepath, domains, suffixes):
    entries = sorted(set(f"'{d}'" for d in domains)) + sorted(set(f"'+.{s}'" for s in suffixes))
    if not entries:
        return 0
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("payload:\n")
        for e in entries:
            f.write(f"  - {e}\n")
    return len(entries)


def write_ipcidr(filepath, ipv4, ipv6):
    entries = sorted(set(ipv4)) + sorted(set(ipv6))
    if not entries:
        return 0
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("payload:\n")
        for e in entries:
            f.write(f"  - '{e}'\n")
    return len(entries)


def write_keywords(filepath, keywords):
    kws = sorted(set(keywords))
    if not kws:
        return 0
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("payload:\n")
        for kw in kws:
            f.write(f"  - DOMAIN-KEYWORD,{kw}\n")
    return len(kws)


# --- Main ---

def process(name, parsed):
    gen = {}
    n = write_domain(os.path.join(RULES_DIR, f"{name}.yaml"), parsed["domains"], parsed["suffixes"])
    if n:
        gen["domain"] = n
    n = write_ipcidr(os.path.join(RULES_DIR, f"{name}-ip.yaml"), parsed["ipv4"], parsed["ipv6"])
    if n:
        gen["ipcidr"] = n
    n = write_keywords(os.path.join(RULES_DIR, f"{name}-kw.yaml"), parsed["keywords"])
    if n:
        gen["keywords"] = n
    return gen


def main():
    os.makedirs(RULES_DIR, exist_ok=True)

    print("=== RuleGo (Local/Remote Surge Lists) ===")
    for name, rel_path in RULEGO_SERVICES.items():
        local_path = os.path.join(LOCAL_SURGE_DIR, rel_path)
        url = f"{RULEGO_REMOTE}/{rel_path}"
        print(f"  {name} ...", end=" ", flush=True)
        content = get_content(url, local_path=local_path)
        if content:
            gen = process(name, parse_surge_list(content))
            print(", ".join(f"{v} {k}" for k, v in gen.items()) or "empty")
        else:
            print("FAILED")

    print("\n=== blackmatrix7 ===")
    for name, path in BM7_SERVICES.items():
        url = f"{BLACKMATRIX7}/{path}"
        print(f"  {name} ...", end=" ", flush=True)
        content = get_content(url)
        if content:
            gen = process(name, parse_classical(content))
            print(", ".join(f"{v} {k}" for k, v in gen.items()) or "empty")
        else:
            print("FAILED")

    # Summary
    print("\n=== Generated files ===")
    for f in sorted(os.listdir(RULES_DIR)):
        if f in ("proxy-extra.yaml", "direct-extra.yaml"):
            continue
        path = os.path.join(RULES_DIR, f)
        size = os.path.getsize(path)
        print(f"  {f:30s} {size:>6d} bytes")


if __name__ == "__main__":
    main()
