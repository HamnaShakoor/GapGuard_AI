"""Sample requirements text (National AI Excellence Scholarship 2026).

Used ONLY for local testing of the RAG module (tests + scripts/rag_demo.py).
Member 6 owns the official demo requirements PDF in data/requirements/.

Formatting convention the chunker relies on (tell Member 6!):
  * Headings:      "Section 4: Required Documents"   or   "4. REQUIRED DOCUMENTS"
  * List items:    start with "- " (dash) or "(a)" -- NOT "1." (that looks like a heading)
"""

SAMPLE_PAGES = [
    # ---- page 1 ----
    """NATIONAL AI EXCELLENCE SCHOLARSHIP 2026
Application Guidelines

Section 1: About the Scholarship
The National AI Excellence Scholarship supports outstanding undergraduate
students in Artificial Intelligence and related fields across Pakistan.
Selected scholars receive full tuition support and a monthly stipend.

Section 2: Eligibility Criteria
- Applicants must be Pakistani citizens holding a valid CNIC.
- Applicants must be currently enrolled in a BS program in AI, Data Science
  or Computer Science at a HEC-recognized university.
- A minimum CGPA of 3.0 out of 4.0 is required.
- Applicants must be under 25 years of age on 1 October 2026.
""",
    # ---- page 2 ----
    """Section 3: Required Documents
All of the following documents are mandatory. Incomplete applications are rejected.
- CNIC: clear copy of the national identity card (front and back).
- University transcript: official transcript showing the CGPA.
- CV: updated curriculum vitae, maximum two pages.
- Photograph: recent passport-size photograph with a plain background.
- Proof of enrollment: enrollment certificate issued by the university.
- Income certificate: official certificate of household income.
- Recommendation letter: see Section 4.
- Personal statement: see Section 5.

Section 4: Recommendation Letter
One recommendation letter is required. The letter must be written by an
academic referee, such as a professor or the head of department, and must be
signed and dated within the last six months.

Section 5: Personal Statement
Applicants must submit a personal statement of 500 words explaining their
motivation, academic goals and how the scholarship will help them contribute
to the field of Artificial Intelligence in Pakistan.
""",
    # ---- page 3 ----
    """Section 6: Financial Information
The income certificate must show a household monthly income below PKR 100,000.
Selected scholars receive a stipend of PKR 40,000 per month and full tuition
fee coverage for the remaining semesters of their degree.

Section 7: Deadlines
Applications close on 30 October 2026 at 11:59 PM PKT. Late applications will
not be considered. Shortlisted candidates will be notified by 15 November 2026.

Section 8: Special Conditions
Scholars must maintain a minimum CGPA of 3.0 every semester. Providing false
information or forged documents results in immediate disqualification.
""",
]
