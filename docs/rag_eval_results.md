# RAG retrieval evaluation (measured)

- Backend: onnx | PDF: sample_scholarship_requirements.pdf | chunks: 9
- Hit@1: 10/10
- Hit@3: 10/10
- Top-1 with correct section AND page: 10/10
- Chunk category labels correct: 6/6

| Query | Category filter | Expected section | Top result | Result |
|---|---|---|---|---|
| recommendation letter from an academic referee | documents | Recommendation Letter | Section 4: Recommendation Letter (p2) | PASS |
| personal statement word limit | documents | Personal Statement | Section 5: Personal Statement (p2) | PASS |
| list of mandatory documents | documents | Required Documents | Section 3: Required Documents (p2) | PASS |
| application deadline date | deadline | Deadlines | Section 7: Deadlines (p3) | PASS |
| when will shortlisted candidates be notified | deadline | Deadlines | Section 7: Deadlines (p3) | PASS |
| household income limit | financial | Financial Information | Section 6: Financial Information (p3) | PASS |
| monthly stipend amount | financial | Financial Information | Section 6: Financial Information (p3) | PASS |
| minimum CGPA required | eligibility | Eligibility Criteria | Section 2: Eligibility Criteria (p1) | PASS |
| age limit for applicants | eligibility | Eligibility Criteria | Section 2: Eligibility Criteria (p1) | PASS |
| forged documents disqualification | - | Special Conditions | Section 8: Special Conditions (p3) | PASS |

Note: 10 queries over one synthetic requirements document (9 chunks). These results are
indicative of this test set only, not a general accuracy claim.