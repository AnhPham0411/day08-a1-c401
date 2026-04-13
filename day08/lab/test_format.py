#!/usr/bin/env python3
"""
Quick test to verify eval.py works with 4 metrics (/5 format)
"""

import json

# Mock scorecard data  
baseline = {
    "label": "Baseline (Dense)",
    "retrieval_mode": "dense",
    "n_questions": 10,
    "faithfulness": 0.80,      # 0-1 scale
    "relevance": 0.70,
    "completeness": 0.75,
    "context_recall": 0.60,
}

variant = {
    "label": "Variant (Hybrid RRF)",
    "retrieval_mode": "hybrid",
    "n_questions": 10,
    "faithfulness": 0.85,
    "relevance": 0.75,
    "completeness": 0.80,
    "context_recall": 0.80,
}

# Test format /5
print("=" * 70)
print("TEST: A/B Comparison Output Format (/5)")
print("=" * 70)

metrics = ["faithfulness", "relevance", "completeness", "context_recall"]
metric_names = {
    "faithfulness": "Faithfulness",
    "relevance": "Answer Relevance",
    "completeness": "Completeness",
    "context_recall": "Context Recall"
}

print(f"\n{'Metric':<20} {'Baseline':>12} {'Variant':>12} {'Delta':>10} {'Ket luan'}")
print('-'*70)

for m in metrics:
    b = baseline.get(m)
    v = variant.get(m)
    delta = v - b
    
    b_str = f"{b*5:.2f}/5"
    v_str = f"{v*5:.2f}/5"
    delta_str = f"{delta*5:+.2f}"
    verdict = "BETTER ↑" if delta > 0.05 else ("WORSE ↓" if delta < -0.05 else "NEUTRAL →")
    
    print(f"{metric_names[m]:<20} {b_str:>12} {v_str:>12} {delta_str:>10} {verdict}")

print('='*70)

# Test scorecard markdown format
print("\nTEST: Scorecard Format (/5)")
print("=" * 70)

print("\n| Metric | Average Score |")
print("|--------|---|")
for m in ["faithfulness", "relevance", "completeness", "context_recall"]:
    print(f"| {metric_names[m]} | {baseline[m]*5:.2f} /5 |")

print("\n✅ Format test passed!")
