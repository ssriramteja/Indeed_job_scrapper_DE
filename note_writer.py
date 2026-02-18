from datetime import date
import os

def save_jobs_to_note(jobs: list):
    """
    Writes the ranked jobs to a markdown file.
    """
    today = date.today().strftime("%Y-%m-%d")
    output_dir = "results"
    
    # Create directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    filename = os.path.join(output_dir, f"job_matches_{today}.md")
    
    # Markdown header
    content = f"# 🎯 Daily Job Matches — {today}\n\n"
    content += f"**Total Jobs Found:** {len(jobs)}\n"
    content += "Jobs posted in the last 24 hours, ranked by resume match score.\n\n"
    content += "---\n\n"
    
    for i, job in enumerate(jobs, 1):
        score = job.get('score', 0)
        title = job.get('title', 'N/A')
        company = job.get('company', 'N/A')
        location = job.get('location', 'N/A')
        link = job.get('apply_link', '#')
        keywords = ", ".join(job.get('matched_keywords', []))
        
        content += f"## {i}. {title} @ {company}\n"
        content += f"**Match Score:** {score}%\n\n"
        content += f"📍 **Location:** {location}\n\n"
        content += f"🔑 **Keywords:** {keywords}\n\n"
        content += f"[Apply Here]({link})\n\n"
        content += "---\n\n"

    # Write to file
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"Successfully saved {len(jobs)} jobs to {filename}")
    return filename

import pandas as pd

def save_jobs_to_excel(jobs: list):
    """
    Writes the ranked jobs to an Excel file.
    """
    if not jobs:
        return None
        
    today = date.today().strftime("%Y-%m-%d")
    output_dir = "results"
    
    # Create directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    filename = os.path.join(output_dir, f"job_matches_{today}.xlsx")
    
    # Prepare data for DataFrame
    df_data = []
    for job in jobs:
        df_data.append({
            "Title": job.get("title"),
            "Company": job.get("company"),
            "Location": job.get("location"),
            "Match Score (%)": job.get("score"),
            "Matched Keywords": ", ".join(job.get("matched_keywords", [])),
            "Posted At": job.get("posted_at"),
            "Apply Link": job.get("apply_link")
        })
    
    df = pd.DataFrame(df_data)
    
    # Write to Excel
    df.to_excel(filename, index=False)
    
    print(f"Successfully saved {len(jobs)} jobs to {filename}")
    return filename

