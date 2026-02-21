# ============================================================
# main.py — CLI entrypoint supporting 4 modes
# ============================================================

import argparse
import sys
from config import OLLAMA_MODEL, OLLAMA_BASE_URL


def print_result(result: dict):
    """Pretty-print a RAG result to the console."""
    print("\n" + "="*70)
    print(f"QUERY: {result['query']}")
    print("-"*70)

    confidence = result.get("confidence", "unknown")
    confidence_display = {
        "high": "\u2705 HIGH — Fully grounded",
        "medium": "\u26a0\ufe0f  MEDIUM — Partially grounded",
        "low": "\u2139\ufe0f  LOW — Limited coverage",
    }
    print(f"CONFIDENCE       : {confidence_display.get(confidence, confidence)}")

    stats = result.get("retrieval_stats", {})
    meta = result.get("metadata_used", {})

    print(f"RETRIEVED CHUNKS : {stats.get('stage1_count', 0)} initially")
    print(f"AFTER THRESHOLD  : {stats.get('threshold_passed', 0)} passed similarity gate")
    print(f"AFTER RERANKING  : {stats.get('rerank_passed', 0)} passed rerank gate")
    print(f"FINAL CHUNKS USED: {stats.get('final_count', 0)}")
    print(f"TOP RERANK SCORE : {stats.get('top_rerank_score', 0):.3f}")
    print(f"PAGES USED       : {meta.get('pages', [])}")
    print(f"SECTIONS USED    : {meta.get('sections', [])}")
    print(f"CONDITIONS TAGGED: {meta.get('conditions', [])}")

    validation = result.get("validation", {})
    if validation.get("hallucination_flag"):
        print(f"\u26a0 HALLUCINATION WARNING: Unverified numbers: "
              f"{validation.get('hallucinated_numbers')}")

    print("-"*70)
    print("ANSWER:")
    print(result["answer"])
    print("="*70)


def check_ollama():
    """Verify Ollama is running before proceeding."""
    import requests
    try:
        r = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        models = [m["name"] for m in r.json().get("models", [])]
        if not any(OLLAMA_MODEL.split(":")[0] in m for m in models):
            print(f"\u26a0 Model '{OLLAMA_MODEL}' not found in Ollama.")
            print(f"  Run: ollama pull {OLLAMA_MODEL}")
            sys.exit(1)
        print(f"[OK] Ollama running. Model '{OLLAMA_MODEL}' available.")
    except Exception:
        print("ERROR: Cannot connect to Ollama.")
        print("  Start Ollama: ollama serve")
        print(f"  Pull model  : ollama pull {OLLAMA_MODEL}")
        print("  Pull embed  : ollama pull nomic-embed-text")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Medical RAG for High-Risk Pregnancy PDF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes:
  --ingest              Parse PDF, embed, and store in FAISS index
  --query "..."         Run a single query
  --interactive         Start interactive REPL
  --evaluate            Run full evaluation test suite

Examples:
  python main.py --ingest
  python main.py --query "What is the prevalence of HRP in India?"
  python main.py --interactive
  python main.py --evaluate
        """
    )
    parser.add_argument("--ingest", action="store_true",
                        help="Parse and index the PDF into FAISS")
    parser.add_argument("--query", type=str, metavar="QUESTION",
                        help="Run a single query through the RAG pipeline")
    parser.add_argument("--interactive", action="store_true",
                        help="Start interactive query loop")
    parser.add_argument("--evaluate", action="store_true",
                        help="Run evaluation test suite")
    parser.add_argument("--production", action="store_true",
                        help="Use production pipeline (4-layer architecture)")

    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        sys.exit(0)

    # --- INGEST MODE ---
    if args.ingest:
        check_ollama()
        from ingest import run_ingestion
        run_ingestion()

    # --- SINGLE QUERY MODE ---
    elif args.query:
        check_ollama()
        
        if args.production:
            # Use production pipeline
            from production_pipeline import ProductionRAGPipeline
            pipeline = ProductionRAGPipeline()
            result = pipeline.run(args.query, verbose=True)
            pipeline.print_result(result)
        else:
            # Use final pipeline
            from final_rag_pipeline import FinalRAGPipeline
            pipeline = FinalRAGPipeline()
            result = pipeline.run(args.query, debug=True, verbose=True)
            print(pipeline.format_result(result, include_debug=True))

    # --- INTERACTIVE MODE ---
    elif args.interactive:
        check_ollama()
        
        if args.production:
            # Use production pipeline
            from production_pipeline import ProductionRAGPipeline
            pipeline = ProductionRAGPipeline()
            print("\nProduction Medical RAG — Interactive Mode")
            print("Type your question and press Enter. Type 'exit' to quit.\n")
            while True:
                try:
                    query = input("Query> ").strip()
                    if not query:
                        continue
                    if query.lower() in ["exit", "quit", "q"]:
                        print("Exiting.")
                        break
                    result = pipeline.run(query, verbose=True)
                    pipeline.print_result(result)
                except KeyboardInterrupt:
                    print("\nExiting.")
                    break
        else:
            # Use final pipeline
            from final_rag_pipeline import FinalRAGPipeline
            pipeline = FinalRAGPipeline()
            print("\nFinal Production RAG — Interactive Mode")
            print("Type your question and press Enter. Type 'exit' to quit.\n")
            while True:
                try:
                    query = input("Query> ").strip()
                    if not query:
                        continue
                    if query.lower() in ["exit", "quit", "q"]:
                        print("Exiting.")
                        break
                    result = pipeline.run(query, debug=False, verbose=True)
                    print(pipeline.format_result(result, include_debug=False))
                except KeyboardInterrupt:
                    print("\nExiting.")
                    break

    # --- EVALUATE MODE ---
    elif args.evaluate:
        check_ollama()
        from evaluate import run_evaluation
        run_evaluation()


if __name__ == "__main__":
    main()
