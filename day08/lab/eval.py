"""
eval.py — Sprint 4: Evaluation Loop
=====================================
Loop: run_rag_answer → cham scorecard → compare_ab

3 metrics (theo slide):
  - Faithfulness   : answer co bam sat context khong? (khong bia)
  - Relevance      : answer co tra loi dung cau hoi khong?
  - Context Recall : expected source co duoc retrieve khong?

Cach chay:
  python eval.py                  # Chay toan bo vong lap
  python eval.py --mode baseline  # Chi chay baseline
  python eval.py --mode variant   # Chi chay variant
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from dotenv import load_dotenv
load_dotenv()

from rag_answer import rag_answer
from openai import OpenAI
import time
from dotenv import load_dotenv
import os

# =============================================================================
# CAU HINH A/B
# A/B Rule: Chi doi MOT bien moi lan
# =============================================================================

load_dotenv()

TEST_QUESTIONS_PATH = Path(__file__).parent / "data" / "test_questions.json"
RESULTS_DIR = Path(__file__).parent / "results"
LOGS_DIR = Path(__file__).parent / "logs"

# Cấu hình baseline (Sprint 2)
BASELINE_CONFIG = {
    "retrieval_mode": "dense",
    "top_k_search":   10,
    "top_k_select":   3,
    "use_rerank":     False,
}

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_test_llm(messages, model=os.getenv("LLM_MODEL"), temperature=0):
    start = time.time()

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )

    content = response.choices[0].message.content
    latency = time.time() - start

    return content, latency

# Cấu hình variant (Sprint 3 — điều chỉnh theo lựa chọn của nhóm)
# TODO Sprint 4: Cập nhật VARIANT_CONFIG theo variant nhóm đã implement
VARIANT_CONFIG = {
    "retrieval_mode": "hybrid",   # Bien duy nhat thay doi
    "top_k_search":   10,
    "top_k_select":   5,
    "use_rerank":     True,
}


# =============================================================================
# SCORING FUNCTIONS
# 4 metrics từ slide: Faithfulness, Answer Relevance, Context Recall, Completeness
# =============================================================================

def score_faithfulness(
    answer: str,
    chunks_used: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Faithfulness: Câu trả lời có bám đúng chứng cứ đã retrieve không?
    Câu hỏi: Model có tự bịa thêm thông tin ngoài retrieved context không?

    Thang điểm 1-5:
      5: Mọi thông tin trong answer đều có trong retrieved chunks
      4: Gần như hoàn toàn grounded, 1 chi tiết nhỏ chưa chắc chắn
      3: Phần lớn grounded, một số thông tin có thể từ model knowledge
      2: Nhiều thông tin không có trong retrieved chunks
      1: Câu trả lời không grounded, phần lớn là model bịa
    """
    # Sprint 4: Implement scoring
    # Tạm thời trả về None (yêu cầu chấm thủ công)
    prompt = f"""
    Given these retrieved chunks: {chunks_used}
    And this answer: {answer}
    Rate the faithfulness on a scale of 1-5.
    5: All information in the answer is in the retrieved chunks
    4: Almost entirely grounded, one small detail is uncertain
    3: Mostly grounded, some information may come from model knowledge
    2: Much information is not in the retrieved chunks
    1: The answer is not grounded, mostly fabricated by the model
    Output JSON: {'score': <int>, 'reason': '<string>'}
    """

    content, latency = call_test_llm(
        [{"role": "user", "content": prompt}],
        temperature=0
    )

    parsed = json.loads(content)
    return parsed


def score_answer_relevance(
    query: str,
    answer: str,
) -> Dict[str, Any]:
    """
    Answer Relevance: Answer có trả lời đúng câu hỏi người dùng hỏi không?
    Câu hỏi: Model có bị lạc đề hay trả lời đúng vấn đề cốt lõi không?

    Thang điểm 1-5:
      5: Answer trả lời trực tiếp và đầy đủ câu hỏi
      4: Trả lời đúng nhưng thiếu vài chi tiết phụ
      3: Trả lời có liên quan nhưng chưa đúng trọng tâm
      2: Trả lời lạc đề một phần
      1: Không trả lời câu hỏi

    Sprint 4: Implement tương tự score_faithfulness
    """
    prompt = f"""
    Given the query: {query}
    And this answer: {answer}
    Rate the answer relevance on a scale of 1-5.
    5: Answer directly and completely to the question
    4: Answer is correct but lacks some supporting details
    3: Answer is relevant but not focused
    2: Answer is partially off-topic
    1: No answer to the question
    Output JSON: {'score': <int>, 'reason': '<string>'}
    """

    content, latency = call_test_llm(
        [{"role": "user", "content": prompt}],
        temperature=0
    )
    
    parsed = json.loads(content)
    return parsed


def score_context_recall(
    chunks_used: List[Dict[str, Any]],
    expected_sources: List[str],
) -> Dict[str, Any]:
    """
    Context Recall: Retriever có mang về đủ evidence cần thiết không?
    Câu hỏi: Expected source có nằm trong retrieved chunks không?

    Đây là metric đo retrieval quality, không phải generation quality.

    Cách tính đơn giản:
        recall = (số expected source được retrieve) / (tổng số expected sources)
    """
    if not expected_sources:
        return {"score": None, "recall": None, "notes": "No expected sources"}

    retrieved_sources = {
        c.get("metadata", {}).get("source", "")
        for c in chunks_used
    }

    # Kiểm tra matching theo partial path (vì source paths có thể khác format)
    found = 0
    missing = []
    for expected in expected_sources:
        expected_name = expected.split("/")[-1].replace(".pdf", "").replace(".md", "")
        matched = any(expected_name.lower() in r.lower() for r in retrieved_sources)
        if matched:
            found += 1
        else:
            missing.append(expected)

    recall = found / len(expected_sources) if expected_sources else 0

    return {
        "score": round(recall * 5),  # Convert to 1-5 scale
        "recall": recall,
        "found": found,
        "missing": missing,
        "notes": f"Retrieved: {found}/{len(expected_sources)} expected sources" +
                 (f". Missing: {missing}" if missing else ""),
    }


def score_completeness(
    query: str,
    answer: str,
    expected_answer: str,
) -> Dict[str, Any]:
    """
    Completeness: Answer có thiếu điều kiện ngoại lệ hoặc bước quan trọng không?
    Câu hỏi: Answer có bao phủ đủ thông tin so với expected_answer không?

    Thang điểm 1-5:
      5: Answer bao gồm đủ tất cả điểm quan trọng trong expected_answer
      4: Thiếu 1 chi tiết nhỏ
      3: Thiếu một số thông tin quan trọng
      2: Thiếu nhiều thông tin quan trọng
      1: Thiếu phần lớn nội dung cốt lõi

    Sprint 4:
    Option 1 — Chấm thủ công: So sánh answer vs expected_answer và chấm.
    Option 2 — LLM-as-Judge:
        "Compare the model answer with the expected answer.
         Rate completeness 1-5. Are all key points covered?
         Output: {'score': int, 'missing_points': [str]}"
    """
    prompt = f"""
    Given the query: {query}
    Given the actual answer: {answer}
    And expected answer: {expected_answer}
    Rate the answer relevance between actual answer and expected answer on a scale of 1-5.
    5: The actual answer includes all the important points in the expected answer.
    4: Missing one small detail.
    3: Missing some important information.
    2: Missing a lot of important information.
    1: Missing most of the core content.
    Output JSON: {'score': int, 'missing_points': [str]}
    """

    content, latency = call_test_llm(
        [{"role": "user", "content": prompt}],
        temperature=0
    )
    
    parsed = json.loads(content)
    return parsed


# =============================================================================
# STEP 1: CHAY PIPELINE
# =============================================================================

def run_pipeline(questions: List[Dict], config: Dict, label: str = "") -> List[Dict]:
    """
    Chay rag_answer() cho toan bo danh sach cau hoi voi config cho truoc.
    Tra ve list ket qua kem thong tin cham diem.
    """
    if test_questions is None:
        with open(TEST_QUESTIONS_PATH, "r", encoding="utf-8") as f:
            test_questions = json.load(f)

    log = []
    results = []
    print(f"\n{'='*50}")
    print(f"Chay pipeline: {label or config['retrieval_mode']}")
    print(f"Config: {config}")
    print('='*50)

    for i, q in enumerate(questions, 1):
        qid             = q.get("id", f"q{i:02d}")
        question        = q.get("question", "")
        expected_answer = q.get("expected_answer", "")
        expected_sources= q.get("expected_sources", [])
        if "expected_source" in q and not expected_sources:
            expected_sources = [q["expected_source"]]
        category        = q.get("category", "general")

        print(f"\n[{i}/{len(questions)}] {qid}: {question[:60]}...")

        # FIX: khởi tạo giá trị mặc định trước try/except
        answer = ""
        sources = []
        chunks_used = []

        try:
            result = rag_answer(
                query          = question,
                retrieval_mode = config["retrieval_mode"],
                top_k_search   = config["top_k_search"],
                top_k_select   = config["top_k_select"],
                use_rerank     = config["use_rerank"],
                verbose        = False,
            )
            answer      = result["answer"]
            sources     = result["sources"]
            chunks_used = result["chunks_used"]

        except Exception as e:
            answer  = f"PIPELINE_ERROR: {e}"
            sources = []
            chunks_used = []

        faith     = score_faithfulness(answer, chunks_used)
        relevance = score_answer_relevance(question, answer)
        recall    = score_context_recall(chunks_used, expected_sources)
        complete  = score_completeness(question, answer, expected_answer)

        row = {
            "id":                   qid,
            "category":             category,
            "query":                question,   # key là "query"
            "answer":               answer,
            "expected_answer":      expected_answer,
            "sources":              sources,
            "chunks_retrieved":     len(chunks_used),
            "faithfulness":         faith["score"],
            "faithfulness_notes":   faith["notes"],
            "relevance":            relevance["score"],
            "relevance_notes":      relevance["notes"],
            "context_recall":       recall.get("score", 0),
            "context_recall_notes": recall["notes"],
            "completeness":         complete["score"],
            "completeness_notes":   complete["notes"],
            "config_label":         label,
            "retrieval_mode":       config["retrieval_mode"],
            "timestamp":            datetime.now().isoformat(),
        }
        results.append(row)
        
        log.append({
            "id": question_id,
            "question": query,
            "answer": answer,
            "sources": result["sources"],
            "chunks_retrieved": len(chunks_used),
            "retrieval_mode": result["config"]["retrieval_mode"],
            "timestamp": datetime.now().isoformat(),
        })

        print(f"  Answer: {answer[:100]}...")
        print(f"  Faithful: {faith['score']} | Relevant: {relevance['score']} | "
              f"Recall: {recall['score']} | Complete: {complete['score']}")

    with open("logs/grading_run.json", "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

    # Tính averages (bỏ qua None)
    for metric in ["faithfulness", "relevance", "context_recall", "completeness"]:
        scores = [r[metric] for r in results if r[metric] is not None]
        avg = sum(scores) / len(scores) if scores else None
        print(f"\nAverage {metric}: {avg:.2f}" if avg else f"\nAverage {metric}: N/A (chưa chấm)")

    return results


def _check_context_recall(expected_source: str, chunks: List[Dict]) -> bool:
    """Context Recall: expected_source co nam trong retrieved chunks khong."""
    if not expected_source:
        return None
    retrieved = [c.get("metadata", {}).get("source", "") for c in chunks]
    return any(expected_source in s for s in retrieved)


# =============================================================================
# STEP 2: CHAM SCORECARD
# =============================================================================

def score_with_llm(results: List[Dict]) -> List[Dict]:
    """
    LLM-as-Judge: cham Faithfulness va Relevance cho tung cau.
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    for r in results:
        if "PIPELINE_ERROR" in r["answer"]:
            r["faithfulness"] = 0
            r["relevance"]    = 0
            continue

        prompt = f"""Cham diem cau tra loi sau day theo 2 tieu chi.

Cau hoi: {r['query']}
Cau tra loi: {r['answer']}

Tra loi ONLY bang JSON, khong giai thich:
{{
  "faithfulness": 1 hoac 0,
  "relevance":    1 hoac 0,
  "note": "mo ta ngan"
}}"""

        try:
            resp = client.chat.completions.create(
                model       = "gpt-4o-mini",
                messages    = [{"role": "user", "content": prompt}],
                temperature = 0,
                max_tokens  = 150,
            )
            raw    = resp.choices[0].message.content.strip()
            raw    = raw.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(raw)
            r["faithfulness"] = int(parsed.get("faithfulness", 0))
            r["relevance"]    = int(parsed.get("relevance",    0))
            r["llm_note"]     = parsed.get("note", "")
        except Exception as e:
            print(f"  [LLM Judge loi] {e} — danh 0")
            r["faithfulness"] = 0
            r["relevance"]    = 0

    return results


def score_manually(results: List[Dict]) -> List[Dict]:
    """
    Cham thu cong: in tung cau, nguoi dung nhap 1/0.
    """
    print("\n=== Cham thu cong (nhap 1=dat / 0=khong dat) ===")
    for r in results:
        print(f"\n[{r['id']}] {r['query']}")
        print(f"Expected: {r['expected_answer']}")
        print(f"Got:      {r['answer']}")

        try:
            r["faithfulness"] = int(input("  Faithfulness (1/0): ").strip())
            r["relevance"]    = int(input("  Relevance    (1/0): ").strip())
        except (ValueError, KeyboardInterrupt):
            r["faithfulness"] = 0
            r["relevance"]    = 0

    return results


# =============================================================================
# STEP 3: TONG KET SCORECARD
# =============================================================================

def compute_scorecard(results: List[Dict], label: str = "") -> Dict:
    """
    Tinh tong hop 3 metrics tren toan bo test set.
    """
    n = len(results)
    if n == 0:
        return {}

    faithfulness_scores = [r["faithfulness"] for r in results if r["faithfulness"] is not None]
    relevance_scores    = [r["relevance"]    for r in results if r["relevance"]    is not None]
    recall_scores       = [r["context_recall"] for r in results if r["context_recall"] is not None]

    scorecard = {
        "label":          label,
        "n_questions":    n,
        "faithfulness":   round(sum(faithfulness_scores) / len(faithfulness_scores), 3) if faithfulness_scores else None,
        "relevance":      round(sum(relevance_scores)    / len(relevance_scores),    3) if relevance_scores    else None,
        "context_recall": round(sum(recall_scores)       / len(recall_scores),       3) if recall_scores       else None,
        "retrieval_mode": results[0]["retrieval_mode"] if results else "unknown",
    }

    print(f"\n{'='*50}")
    print(f"SCORECARD: {label}")
    print(f"  Faithfulness   : {scorecard['faithfulness']:.2f}/5.0"   if scorecard['faithfulness']   is not None else "  Faithfulness   : N/A")
    print(f"  Relevance      : {scorecard['relevance']:.2f}/5.0"      if scorecard['relevance']      is not None else "  Relevance      : N/A")
    print(f"  Context Recall : {scorecard['context_recall']:.2f}/5.0" if scorecard['context_recall'] is not None else "  Context Recall : N/A")
    print(f"  N questions    : {n}")
    print('='*50)

    return scorecard


# =============================================================================
# STEP 4: COMPARE A/B
# =============================================================================

def compare_ab(scorecard_baseline: Dict, scorecard_variant: Dict) -> None:
    """
    In bang so sanh delta giua baseline va variant.
    Delta duong → variant tot hon.
    """
    metrics = ["faithfulness", "relevance", "context_recall"]

    print(f"\n{'='*60}")
    print("A/B COMPARISON")
    print(f"  Baseline : {scorecard_baseline.get('label')} ({scorecard_baseline.get('retrieval_mode')})")
    print(f"  Variant  : {scorecard_variant.get('label')} ({scorecard_variant.get('retrieval_mode')})")
    print(f"\n{'Metric':<20} {'Baseline':>10} {'Variant':>10} {'Delta':>10} {'Ket luan'}")
    print('-'*60)

    for m in metrics:
        b = scorecard_baseline.get(m)
        v = scorecard_variant.get(m)
        if b is None or v is None:
            print(f"{m:<20} {'N/A':>10} {'N/A':>10} {'N/A':>10}")
            continue
        delta   = v - b
        verdict = "BETTER ↑" if delta > 0.05 else ("WORSE ↓" if delta < -0.05 else "NEUTRAL →")
        print(f"{m:<20} {b:>10.2f} {v:>10.2f} {delta:>+10.2f} {verdict}")

    print('='*60)
    print("\nKet luan cho tuning-log.md:")
    improvements = [m for m in metrics
                    if scorecard_variant.get(m) and scorecard_baseline.get(m)
                    and scorecard_variant[m] - scorecard_baseline[m] > 0.05]
    regressions  = [m for m in metrics
                    if scorecard_variant.get(m) and scorecard_baseline.get(m)
                    and scorecard_variant[m] - scorecard_baseline[m] < -0.05]

    if improvements:
        print(f"  Variant tot hon o: {', '.join(improvements)}")
    if regressions:
        print(f"  Variant kem hon o: {', '.join(regressions)}")
    if not improvements and not regressions:
        print("  Khong co su khac biet dang ke (delta < 5%)")


# =============================================================================
# STEP 5: LUU KET QUA
# =============================================================================

def save_scorecard_md(results: List[Dict], scorecard: Dict, filename: str) -> None:
    """Luu scorecard ra file .md theo format SCORING.md yeu cau."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    path = RESULTS_DIR / filename

    lines = [
        f"# Scorecard — {scorecard.get('label', '')}",
        f"",
        f"**Retrieval mode:** `{scorecard.get('retrieval_mode')}`  ",
        f"**N questions:** {scorecard.get('n_questions')}  ",
        f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"",
        f"## Tong ket metrics",
        f"",
        f"| Metric | Score |",
        f"|--------|-------|",
        f"| Faithfulness   | {scorecard.get('faithfulness', 'N/A'):.2f}/5.0 |" if scorecard.get('faithfulness') is not None else "| Faithfulness   | N/A |",
        f"| Relevance      | {scorecard.get('relevance',    'N/A'):.2f}/5.0 |" if scorecard.get('relevance')    is not None else "| Relevance      | N/A |",
        f"| Context Recall | {scorecard.get('context_recall', 'N/A'):.2f}/5.0 |" if scorecard.get('context_recall') is not None else "| Context Recall | N/A |",
        f"",
        f"## Chi tiet tung cau",
        f"",
        f"| ID | Question | Faithful | Relevant | Recall | Answer preview |",
        f"|----|----------|----------|----------|--------|----------------|",
    ]

    for r in results:
        f_score = r.get("faithfulness", "-")
        r_score = r.get("relevance",    "-")
        recall  = "✓" if r.get("context_recall") else ("✗" if r.get("context_recall") is False else "-")
        preview = r["answer"][:60].replace("|", "/")
        lines.append(f"| {r['id']} | {r['query'][:40]} | {f_score} | {r_score} | {recall} | {preview}... |")

    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved: {path}")


def save_grading_log(results: List[Dict], filename: str = "grading_run.json") -> None:
    """Luu grading_run.json theo format SCORING.md yeu cau."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    path = LOGS_DIR / filename

    log = [
        {
            "id":               r["id"],
            "question":         r["query"],           # FIX: đổi r["question"] → r["query"]
            "answer":           r["answer"],
            "sources":          r["sources"],
            "chunks_retrieved": r["chunks_retrieved"],
            "retrieval_mode":   r["retrieval_mode"],
            "timestamp":        r["timestamp"],
        }
        for r in results
    ]

    path.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved: {path}")


# =============================================================================
# MAIN — Vong lap day du
# =============================================================================

def run_scorecard(config: Dict, questions: List[Dict], label: str, use_llm_judge: bool = True) -> tuple:
    """
    Chay toan bo vong lap cho 1 config:
    run_rag_answer → cham scorecard → tra ve (results, scorecard)
    """
    results   = run_pipeline(questions, config, label)
    # if use_llm_judge:
    #     results = score_with_llm(results)
    # else:
    #     results = score_manually(results)
    scorecard = compute_scorecard(results, label)
    return results, scorecard


if __name__ == "__main__":
    mode = "both"
    if len(sys.argv) > 2 and sys.argv[1] == "--mode":
        mode = sys.argv[2]

    if not TEST_QUESTIONS_PATH.exists():
        print(f"Khong tim thay {TEST_QUESTIONS_PATH}")
        print("Tao data/test_questions.json truoc.")
        sys.exit(1)

    with open(TEST_QUESTIONS_PATH, encoding="utf-8") as f:
        questions = json.load(f)

    print(f"Doc duoc {len(questions)} cau hoi tu {TEST_QUESTIONS_PATH}")

    use_llm = bool(os.getenv("OPENAI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    if not use_llm:
        print("Khong co API key → chuyen sang cham thu cong")

    # === CHAY BASELINE ===
    if mode in ("both", "baseline"):
        baseline_results, baseline_scorecard = run_scorecard(
            config        = BASELINE_CONFIG,
            questions     = questions,
            label         = "Baseline (Dense)",
            use_llm_judge = use_llm,
        )
        save_scorecard_md(baseline_results, baseline_scorecard, "scorecard_baseline.md")
        save_grading_log(baseline_results, "grading_run_baseline.json")

    # === CHAY VARIANT ===
    if mode in ("both", "variant"):
        variant_results, variant_scorecard = run_scorecard(
            config        = VARIANT_CONFIG,
            questions     = questions,
            label         = "Variant (Hybrid RRF)",
            use_llm_judge = use_llm,
        )
        save_scorecard_md(variant_results, variant_scorecard, "scorecard_variant.md")
        save_grading_log(variant_results, "grading_run_variant.json")

    # === SO SANH A/B ===
    if mode == "both":
        compare_ab(baseline_scorecard, variant_scorecard)

    print("\nHoan thanh! Ket qua luu trong results/ va logs/")