"""
Packaging Intelligence Engine — Core Scoring Module
GSoC 2026 | Open Food Facts | Tejaswini Pinnamreddy
"""

WEIGHT_PROFILES = {
    "balanced":          { "recyclability": 0.35, "carbon": 0.30, "size_fit": 0.20, "cost": 0.15 },
    "environment-first": { "recyclability": 0.45, "carbon": 0.40, "size_fit": 0.10, "cost": 0.05 },
    "cost-sensitive":    { "recyclability": 0.20, "carbon": 0.20, "size_fit": 0.25, "cost": 0.35 },
}


def filter_packaging_options(product, options):
    """Remove options that violate hard product constraints before scoring."""
    valid = []
    for opt in options:
        if product.get("fragile")    and not opt.get("is_protective"): continue
        if product.get("weight_kg", 0) > opt.get("max_weight_kg", 0): continue
        if product.get("is_liquid")  and not opt.get("liquid_safe"):   continue
        if product.get("perishable") and not opt.get("airtight"):      continue
        valid.append(opt)
    return valid


def normalize(value, min_val, max_val):
    """Normalize a value to [0, 1]. Returns 0 if min == max."""
    if max_val == min_val:
        return 0.0
    return round((value - min_val) / (max_val - min_val), 4)


def normalize_options(options):
    """Normalize all scoring dimensions across candidates."""
    recyclabilities = [o.get("recyclability", 0)     for o in options]
    carbons         = [o.get("carbon_kg_per_unit", 0) for o in options]
    sizes           = [o.get("size_efficiency", 0)    for o in options]
    costs           = [o.get("cost_per_unit", 0)      for o in options]

    result = []
    for opt in options:
        n = dict(opt)
        n["norm_recyclability"] = normalize(opt.get("recyclability", 0),     min(recyclabilities), max(recyclabilities))
        n["norm_carbon"]        = 1.0 - normalize(opt.get("carbon_kg_per_unit", 0), min(carbons), max(carbons))  # lower is better
        n["norm_size_fit"]      = normalize(opt.get("size_efficiency", 0),   min(sizes),  max(sizes))
        n["norm_cost"]          = 1.0 - normalize(opt.get("cost_per_unit", 0), min(costs), max(costs))  # lower is better
        result.append(n)
    return result


def recommend(product, options, mode="balanced"):
    """
    Full pipeline: filter → normalize → score → rank.

    Returns ranked list with per-factor breakdowns.
    Returns empty list if no options pass constraint filtering.
    """
    weights    = WEIGHT_PROFILES.get(mode, WEIGHT_PROFILES["balanced"])
    candidates = filter_packaging_options(product, options)
    if not candidates:
        return []

    candidates = normalize_options(candidates)

    for opt in candidates:
        opt["score"] = round(
            weights["recyclability"] * opt["norm_recyclability"]
            + weights["carbon"]      * opt["norm_carbon"]
            + weights["size_fit"]    * opt["norm_size_fit"]
            + weights["cost"]        * opt["norm_cost"], 4
        )

    ranked = sorted(candidates, key=lambda x: x["score"], reverse=True)
    return [
        {
            "rank":      i + 1,
            "name":      opt["name"],
            "score":     opt["score"],
            "breakdown": {
                "recyclability": opt["norm_recyclability"],
                "carbon":        opt["norm_carbon"],
                "size_fit":      opt["norm_size_fit"],
                "cost":          opt["norm_cost"],
            }
        }
        for i, opt in enumerate(ranked)
    ]


# --- Quick demo ---
if __name__ == "__main__":
    import json

    with open("../data/packaging_options.json") as f:
        options = json.load(f)

    product = { "weight_kg": 0.5, "fragile": True, "is_liquid": True, "perishable": False }

    for mode in ["balanced", "environment-first", "cost-sensitive"]:
        print(f"\n=== Mode: {mode} ===")
        for r in recommend(product, options, mode=mode)[:3]:
            print(f"  #{r['rank']} {r['name']} — score: {r['score']}")
