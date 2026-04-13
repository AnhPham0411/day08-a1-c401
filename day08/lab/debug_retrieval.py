from rag_answer import retrieve_dense

results = retrieve_dense("SLA xu ly ticket P1 la bao lau?", top_k=20)
print(f"Tong so chunks tra ve: {len(results)}\n")
for i, c in enumerate(results, 1):
    section = c["metadata"]["section"]
    score   = c["score"]
    preview = c["text"][:80].replace("\n", " ")
    print(f"[{i:2d}] score={score:.4f} | {section}")
    print(f"      {preview}")
    print()