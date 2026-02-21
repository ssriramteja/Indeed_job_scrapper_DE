from resume_keywords import SEARCH_TITLES
from job_scraper import collect_all_jobs
from ats_scrapers import collect_ats_jobs
from matcher import rank_jobs
from note_writer import save_jobs_to_note, save_jobs_to_excel

def deduplicate_jobs(jobs: list) -> list:
    """
    Deduplicate jobs by apply link URL.
    """
    seen_urls = set()
    unique_jobs = []
    
    for job in jobs:
        url = job.get("job_apply_link")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_jobs.append(job)
        elif not url:
            # Keep jobs without URLs (shouldn't happen but just in case)
            unique_jobs.append(job)
    
    return unique_jobs

def main():
    print("=" * 60)
    print("ENHANCED JOB SCRAPER - Multiple Sources")
    print("=" * 60)
    
    # Collect from traditional job boards
    print("\n[1/2] Fetching jobs from Indeed and ZipRecruiter...")
    traditional_jobs = collect_all_jobs(titles=SEARCH_TITLES, location="United States")
    print(f"✓ Collected {len(traditional_jobs)} jobs from traditional sources")
    
    # Collect from ATS job boards (Workday, Greenhouse, iCIMS)
    print("\n[2/2] Fetching jobs from ATS platforms (Workday, Greenhouse, iCIMS)...")
    ats_jobs = collect_ats_jobs(titles=SEARCH_TITLES, location="United States")
    print(f"✓ Collected {len(ats_jobs)} jobs from ATS platforms")
    
    # Merge all jobs
    all_jobs = traditional_jobs + ats_jobs
    print(f"\n📊 Total jobs before deduplication: {len(all_jobs)}")
    
    # Deduplicate
    unique_jobs = deduplicate_jobs(all_jobs)
    print(f"📊 Unique jobs after deduplication: {len(unique_jobs)}")
    
    if not unique_jobs:
        print("\n❌ No jobs found.")
        return

    # Score and rank (with new title filtering for Principal/Staff/Director)
    print(f"\n🎯 Scoring and ranking {len(unique_jobs)} jobs against resume...")
    print("   Filters: FAANG, Senior Titles (Principal/Staff/Director), >8 yrs exp, Security Clearance")
    ranked = rank_jobs(unique_jobs, min_score=10.0)  # Lowered from 15% to 10% for more results

    if ranked:
        print(f"\n✅ Found {len(ranked)} matching jobs!")
        print(f"🏆 Top match: {ranked[0]['title']} at {ranked[0]['company']} — {ranked[0]['score']}%")
        filename = save_jobs_to_note(ranked)
        excel_filename = save_jobs_to_excel(ranked)
        
        # New requirements: Table in README and Git push
        from note_writer import update_readme_with_jobs, git_push_changes
        update_readme_with_jobs(ranked)
        git_push_changes()
        
        print(f"\n📝 Done! Check '{filename}' and '{excel_filename}' for your daily job matches.")
    else:
        print("\n❌ No matching jobs found today after filtering.")

if __name__ == "__main__":
    main()
