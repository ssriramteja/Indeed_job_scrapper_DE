from datetime import date
import os
import subprocess

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

def update_readme_with_jobs(new_jobs: list):
    """
    Updates the README.md in the root directory with a table of jobs.
    Maintains history for 4 days and avoids duplicates.
    Sorts by latest arrival (Discovery Timestamp).
    """
    from datetime import datetime, timedelta
    
    today_dt = datetime.now()
    # Use full timestamp for discovery
    now_str = today_dt.strftime("%Y-%m-%d %H:%M")
    four_days_ago = today_dt - timedelta(days=4)
    
    # README path
    readme_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md")
    
    existing_jobs = []
    if os.path.exists(readme_path):
        try:
            with open(readme_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            # Find the table rows
            for line in lines:
                if "|" in line and "Company" not in line and ":---" not in line:
                    parts = [p.strip() for p in line.split("|") if p.strip()]
                    if len(parts) >= 6:
                        # Index mapping: 0=Company, 1=Role, 2=Location, 3=Score, 4=Link, 5=Date
                        apply_link_md = parts[4]
                        import re
                        url_match = re.search(r'\[Apply\]\((.*?)\)', apply_link_md)
                        link = url_match.group(1) if url_match else "#"
                        
                        existing_jobs.append({
                            "company": parts[0].replace("\\|", "|"),
                            "title": parts[1].replace("\\|", "|"),
                            "location": parts[2].replace("\\|", "|"),
                            "score": parts[3].replace("%", ""),
                            "apply_link": link,
                            "date_found": parts[5]
                        })
        except Exception as e:
            print(f"⚠️ Warning: Could not parse existing README: {e}")

    # Merge and Deduplicate by apply link
    all_jobs_dict = {}
    
    # Add existing jobs (if not too old)
    for job in existing_jobs:
        try:
            # Parse existing date (could be YYYY-MM-DD or YYYY-MM-DD HH:MM)
            date_found = job["date_found"]
            if " " in date_found:
                job_date = datetime.strptime(date_found, "%Y-%m-%d %H:%M")
            else:
                job_date = datetime.strptime(date_found, "%Y-%m-%d")
                
            if job_date >= four_days_ago:
                all_jobs_dict[job["apply_link"]] = job
        except (ValueError, KeyError):
            continue

    # Add new jobs
    for job in new_jobs:
        link = job.get('apply_link', '#')
        # Only add if it's genuinely new OR if we want to refresh the timestamp for a repeat listing
        # Usually, if it's in the README within 4 days, we consider it "already found".
        if link not in all_jobs_dict:
            all_jobs_dict[link] = {
                "company": job.get('company', 'N/A'),
                "title": job.get('title', 'N/A'),
                "location": job.get('location', 'N/A'),
                "score": str(job.get('score', 0)),
                "apply_link": link,
                "date_found": now_str
            }

    # Sort merged jobs by date_found (descending) then score (descending)
    # We use a custom key to handle string comparison correctly for timestamps
    def sort_key(x):
        d = x["date_found"]
        # Ensure string comparison works by padding if it's just a date
        full_d = d if " " in d else f"{d} 00:00"
        return (full_d, float(x["score"]))

    sorted_jobs = sorted(
        all_jobs_dict.values(), 
        key=sort_key, 
        reverse=True
    )

    # Header and Table structure
    content = f"# 🎯 Job Search Alert System\n\n"
    content += f"Last updated: {now_str}\n\n"
    content += "### 🚀 Daily Job Matches\n\n"
    content += "| Company | Role | Location | Match Score | Application | Date Found |\n"
    content += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
    
    for job in sorted_jobs:
        company = job['company'].replace("|", "\\|")
        title = job['title'].replace("|", "\\|")
        location = job['location'].replace("|", "\\|")
        score = f"{job['score']}%"
        link = job['apply_link']
        date_found = job['date_found']
        
        content += f"| {company} | {title} | {location} | {score} | [Apply]({link}) | {date_found} |\n"
    
    content += "\n\n---\n*Automated job search powered by Indeed & ATS Scrapers.*"
    
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"✓ Updated README.md with {len(sorted_jobs)} jobs (Total from last 4 days)")
    return readme_path

def git_push_changes():
    """
    Adds, commits, and pushes changes to Git.
    """
    # Skip if running in GitHub Actions to avoid redundant pushes and potential loops
    if os.getenv('GITHUB_ACTIONS') == 'true':
        print("\nℹ️ Running in GitHub Actions. Skipping internal git push.")
        return True

    try:
        # Get repo root (where .git is)
        root_dir = os.path.dirname(os.path.abspath(__file__))
        
        print("\n⚙️ Pushing changes to Git...")
        
        # Add changes
        subprocess.run(["git", "add", "."], cwd=root_dir, check=True)
        
        # Commit
        today = date.today().strftime("%Y-%m-%d")
        commit_msg = f"Update job matches: {today}"
        
        # Check if there are changes to commit
        status = subprocess.run(["git", "status", "--porcelain"], cwd=root_dir, capture_output=True, text=True)
        if not status.stdout.strip():
            print("ℹ️ No changes to commit.")
            return True
            
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=root_dir, check=True)
        
        # Push
        subprocess.run(["git", "push"], cwd=root_dir, check=True)
        
        print("🚀 Successfully pushed to Git!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Git error: {e}")
        return False
    except Exception as e:
        print(f"❌ General error: {e}")
        return False

