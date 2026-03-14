#!/usr/bin/env python3
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("--vcf", required=True)
parser.add_argument("--out", required=True)
args = parser.parse_args()

# Mock script: write an empty/mock JSON report
with open(args.out, "w") as f:
    json.dump({"run": "mock", "variants": []}, f)
