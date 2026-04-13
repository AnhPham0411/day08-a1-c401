
from rag_answer import retrieve_hybrid
results = retrieve_hybrid('Contractor cap quyen Admin Access dieu kien gi?', top_k=10)
for i, c in enumerate(results, 1):
    print(i, c['metadata']['section'], c['text'][:60])
