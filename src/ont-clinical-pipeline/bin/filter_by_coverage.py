#!/usr/bin/env python3
import argparse
import shutil

parser = argparse.ArgumentParser()
parser.add_argument("--vcf", required=True)
parser.add_argument("--bed", required=True)
parser.add_argument("--min_cov", required=True)
parser.add_argument("--out", required=True)
args = parser.parse_args()

# Mock script: just copy input VCF to output
shutil.copy(args.vcf, args.out)
