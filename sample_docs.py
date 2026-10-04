import os

def create_sample_documents():
    # Scenario 1: Complete Application
    s1_dir = "sample_documents/scenario_1_complete"
    os.makedirs(s1_dir, exist_ok=True)
    
    with open(f"{s1_dir}/transcript.txt", "w") as f:
        f.write("OFFICIAL TRANSCRIPT\nStudent Name: Alex Taylor\nCumulative GPA: 3.85 / 4.00\nMajor: Computer Science\nStatus: Active")
        
    with open(f"{s1_dir}/cv.txt", "w") as f:
        f.write("ALEX TAYLOR - CURRICULUM VITAE\nEducation: BS Computer Science\nProjects: RAG Pipeline, LLM Agents\nPublications: 1 Workshop Paper")
        
    with open(f"{s1_dir}/recommendation_letter.txt", "w") as f:
        f.write("RECOMMENDATION LETTER\nI strongly recommend Alex Taylor for the National AI Excellence Scholarship 2026 based on outstanding academic performace.\n- Prof. Smith, Department Chair")
        
    with open(f"{s1_dir}/personal_statement.txt", "w") as f:
        f.write("PERSONAL STATEMENT\nMy passion lies in developing ethical AI systems and expanding transformer architectures for real-world impact...")

    # Scenario 2: Missing Documents
    s2_dir = "sample_documents/scenario_2_missing_docs"
    os.makedirs(s2_dir, exist_ok=True)
    
    with open(f"{s2_dir}/transcript.txt", "w") as f:
        f.write("OFFICIAL TRANSCRIPT\nStudent Name: Jordan Lee\nCumulative GPA: 3.70 / 4.00")
        
    with open(f"{s2_dir}/cv.txt", "w") as f:
        f.write("JORDAN LEE - CV\nFocus: Data Science & AI Research")

    # Scenario 3: Warnings / Edge Cases (e.g. low GPA)
    s3_dir = "sample_documents/scenario_3_warnings"
    os.makedirs(s3_dir, exist_ok=True)
    
    with open(f"{s3_dir}/transcript.txt", "w") as f:
        f.write("OFFICIAL TRANSCRIPT\nStudent Name: Casey Morgan\nCumulative GPA: 3.20 / 4.00") # Below 3.5 requirement
        
    with open(f"{s3_dir}/cv.txt", "w") as f:
        f.write("CASEY MORGAN - CV\nExperience: Junior Developer")

    print("Successfully generated sample documents for Scenarios 1, 2, and 3!")

if __name__ == "__main__":
    create_sample_documents()