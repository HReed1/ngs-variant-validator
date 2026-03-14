#!/usr/bin/env python3
import argparse
import json
import gzip

parser = argparse.ArgumentParser()
parser.add_argument("--vcf", required=True)
parser.add_argument("--bed", required=True)
parser.add_argument("--out", required=True)
parser.add_argument("--metrics", required=True)
args = parser.parse_args()

# 1. Parse Mosdepth BED for coverage profile
coverage_data = []
with gzip.open(args.bed, 'rt') as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) >= 4:
            coverage_data.append(float(parts[3]))

# Downsample coverage to ~100 points for the UI chart
step = max(1, len(coverage_data) // 100)
coverage_profile = coverage_data[::step][:100]

# 2. Parse VCF for Quality profile and Variants
quality_profile = []
variants = []
with gzip.open(args.vcf, 'rt') as f:
    for line in f:
        if not line.startswith('#'):
            parts = line.strip().split('\t')
            if len(parts) > 5 and parts[5] != '.':
                qual = float(parts[5])
                quality_profile.append(qual)
                variants.append({
                    "chrom": parts[0],
                    "pos": parts[1],
                    "ref": parts[3],
                    "alt": parts[4],
                    "qual": qual
                })

# Downsample quality to ~100 points
q_step = max(1, len(quality_profile) // 100)
quality_profile = quality_profile[::q_step][:100] if quality_profile else [0] * 100

# 3. Write Metrics JSON (These arrays will be injected into the UI!)
with open(args.metrics, "w") as f:
    json.dump({
        "coverage_profile": coverage_profile,
        "quality_profile": quality_profile
    }, f)

# 4. Write Final Clinical Report
with open(args.out, "w") as f:
    json.dump({"run": "real_execution", "total_variants": len(variants), "variants": variants[:50]}, f)