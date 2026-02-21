# ============================================================
# evaluate.py — Validation test suite with expected answers
# All expected values derived directly from the merged PDF
# ============================================================

from rag_pipeline import run_rag

# ============================================================
# TEST QUERIES — Every expected value comes directly from PDF
# ============================================================
TEST_QUERIES = [
    # --- RESEARCH PAPER QUERIES ---
    {
        "id": "RP-01",
        "query": "What is the overall prevalence of high-risk pregnancy in India?",
        "expected_contains": ["49.4%"],
        "expected_page_type": "research_paper",
        "category": "statistic",
    },
    {
        "id": "RP-02",
        "query": "Which Indian states have the highest prevalence of high-risk pregnancies?",
        "expected_contains": ["Meghalaya", "67.8", "Manipur", "66.7"],
        "expected_page_type": "research_paper",
        "category": "statistic",
    },
    {
        "id": "RP-03",
        "query": "What is the adjusted odds ratio for women with no education and high-risk pregnancy?",
        "expected_contains": ["2.02", "1.84", "2.22"],
        "expected_page_type": "research_paper",
        "category": "statistic",
    },
    {
        "id": "RP-04",
        "query": "What percentage of Indian pregnant women had short birth spacing?",
        "expected_contains": ["31.1"],
        "expected_page_type": "research_paper",
        "category": "statistic",
    },
    {
        "id": "RP-05",
        "query": "What percentage of women had adverse birth outcomes in their last birth?",
        "expected_contains": ["19.5"],
        "expected_page_type": "research_paper",
        "category": "statistic",
    },
    {
        "id": "RP-06",
        "query": "What is the adjusted odds ratio for the poorest wealth quintile and high-risk pregnancy?",
        "expected_contains": ["1.33", "1.18", "1.49"],
        "expected_page_type": "research_paper",
        "category": "statistic",
    },
    {
        "id": "RP-07",
        "query": "What percentage of women had multiple high-risk factors?",
        "expected_contains": ["16.4"],
        "expected_page_type": "research_paper",
        "category": "statistic",
    },

    # --- CLINICAL GUIDELINE QUERIES ---
    {
        "id": "CG-01",
        "query": "What is the first-line drug for hypertension in pregnancy and its dose?",
        "expected_contains": ["Alpha methyl dopa", "250 mg"],
        "expected_page_type": "clinical_guideline",
        "category": "drug_dosage",
    },
    {
        "id": "CG-02",
        "query": "What is the loading dose of magnesium sulfate for eclampsia?",
        "expected_contains": ["4 gm", "5 gm", "IM"],
        "expected_page_type": "clinical_guideline",
        "category": "drug_dosage",
    },
    {
        "id": "CG-03",
        "query": "How is severe anaemia defined in pregnancy and what is its management?",
        "expected_contains": ["7 g", "FRU", "blood transfusion"],
        "expected_page_type": "clinical_guideline",
        "category": "clinical_management",
    },
    {
        "id": "CG-04",
        "query": "What TSH level in first trimester requires hypothyroidism treatment?",
        "expected_contains": ["2.5", "levothyroxine"],
        "expected_page_type": "clinical_guideline",
        "category": "diagnostic_criteria",
    },
    {
        "id": "CG-05",
        "query": "What is the GDM diagnosis threshold and when is the second test done?",
        "expected_contains": ["140 mg", "24-28 weeks"],
        "expected_page_type": "clinical_guideline",
        "category": "diagnostic_criteria",
    },
    {
        "id": "CG-06",
        "query": "What is the treatment for early stage syphilis in pregnancy?",
        "expected_contains": ["2.4 million", "benzathine", "penicillin"],
        "expected_page_type": "clinical_guideline",
        "category": "drug_dosage",
    },

    # --- PROCEDURE CHART QUERIES ---
    {
        "id": "PC-01",
        "query": "What are the steps of Active Management of Third Stage of Labour?",
        "expected_contains": ["Oxytocin 10", "cord traction", "uterine massage"],
        "expected_page_type": "procedure_chart",
        "category": "procedure_steps",
    },
    {
        "id": "PC-02",
        "query": "When should breastfeeding be initiated after delivery?",
        "expected_contains": ["1 hour"],
        "expected_page_type": "procedure_chart",
        "category": "procedure_steps",
    },
    {
        "id": "PC-03",
        "query": "How many minimum antenatal checkups are required during pregnancy?",
        "expected_contains": ["4"],
        "expected_page_type": "procedure_chart",
        "category": "clinical_management",
    },

    # --- GOVERNMENT POLICY QUERIES ---
    {
        "id": "GP-01",
        "query": "What cash benefit is given under Pradhan Mantri Matru Vandana Yojana?",
        "expected_contains": ["5,000", "1000", "2000"],
        "expected_page_type": "government_policy",
        "category": "policy_scheme",
    },
    {
        "id": "GP-02",
        "query": "What is the ASHA incentive under extended PMSMA for HRP follow-up visits?",
        "expected_contains": ["100", "500", "45"],
        "expected_page_type": "government_policy",
        "category": "policy_scheme",
    },
    {
        "id": "GP-03",
        "query": "On which day of every month is the PMSMA clinic conducted?",
        "expected_contains": ["9th"],
        "expected_page_type": "government_policy",
        "category": "policy_scheme",
    },

    # --- CHECKLIST QUERIES ---
    {
        "id": "CL-01",
        "query": "What equipment must be available at a PMSMA clinic?",
        "expected_contains": ["BP Apparatus", "Glucometer", "Fetoscope"],
        "expected_page_type": "monitoring_checklist",
        "category": "checklist",
    },

    # --- OUT OF SCOPE (should return soft-grounded fallback) ---
    {
        "id": "OOS-01",
        "query": "What is the treatment for COVID-19 in pregnancy?",
        "expected_contains": [],
        "expected_confidence": "low",
        "expected_page_type": None,
        "category": "out_of_scope",
    },
    {
        "id": "OOS-02",
        "query": "What is the global maternal mortality rate in 2023?",
        "expected_contains": [],
        "expected_confidence": "low",
        "expected_page_type": None,
        "category": "out_of_scope",
    },
]


def run_evaluation():
    """Run all test queries and print evaluation report."""
    print("\n" + "="*70)
    print("MEDICAL RAG EVALUATION REPORT")
    print("="*70)

    total = len(TEST_QUERIES)
    passed = 0
    failed = 0
    results = []

    for test in TEST_QUERIES:
        print(f"\n[{test['id']}] {test['query'][:70]}...")

        result = run_rag(test["query"], verbose=False)
        answer = result["answer"].lower()
        confidence = result.get("confidence", "unknown")

        all_found = all(exp.lower() in answer for exp in test["expected_contains"])

        retrieved_pages = result["metadata_used"].get("pages", [])
        correct_type_retrieved = True
        if test["expected_page_type"]:
            correct_type_retrieved = result["retrieval_stats"]["final_count"] > 0

        hallucinated = result["validation"].get("hallucination_flag", False)

        if test["category"] == "out_of_scope":
            expected_conf = test.get("expected_confidence", "low")
            status = "PASS" if confidence == expected_conf else "FAIL"
        else:
            status = "PASS" if all_found and not hallucinated else "FAIL"

        if status == "PASS":
            passed += 1
        else:
            failed += 1

        print(f"  Status         : {status}")
        print(f"  Confidence     : {confidence.upper()}")
        print(f"  Pages retrieved: {retrieved_pages}")
        print(f"  Chunks used    : {result['retrieval_stats'].get('final_count', 0)}")
        print(f"  Expected found : {all_found}")
        print(f"  Hallucination  : {hallucinated}")
        if not all_found and test["expected_contains"]:
            print(f"  Missing        : {[e for e in test['expected_contains'] if e.lower() not in answer]}")

        results.append({**test, "status": status, "confidence": confidence,
                        "answer_snippet": result["answer"][:200]})

    print("\n" + "="*70)
    print(f"EVALUATION SUMMARY: {passed}/{total} PASSED | {failed}/{total} FAILED")
    print(f"Accuracy: {passed/total*100:.1f}%")
    print("="*70)

    return results


if __name__ == "__main__":
    run_evaluation()
