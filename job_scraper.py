import pandas as pd
from jobspy import scrape_jobs
import time

def collect_all_jobs(titles: list, location: str = "United States") -> list:
    """
    Scrapes jobs from Indeed and ZipRecruiter using python-jobspy.
    Returns a list of dictionaries.
    """
    all_jobs_df = pd.DataFrame()
    
    # Increased results per title and added ZipRecruiter for more coverage
    # Added delays between requests to avoid rate limiting
    
    print(f"Starting scrape for {len(titles)} titles in {location}...")
    
    for idx, title in enumerate(titles):
        print(f"Scraping for: {title} ({idx+1}/{len(titles)})")
        try:
            jobs: pd.DataFrame = scrape_jobs(
                site_name=["indeed", "zip_recruiter"],  # Removed LinkedIn/Glassdoor (failing with 400 errors)
                search_term=title,
                location=location,
                results_wanted=500, # Increased from 300 to 500 for more coverage
                hours_old=24,       # Restrict to last 24 hours
                country_watchlist=["USA"]
            )
            
            if not jobs.empty:
                all_jobs_df = pd.concat([all_jobs_df, jobs], ignore_index=True)
                print(f"Found {len(jobs)} jobs for {title}")
            else:
                print(f"No jobs found for {title}")
                
            # Add delay between requests to avoid rate limiting (except for last request)
            if idx < len(titles) - 1:
                time.sleep(2)
                
        except Exception as e:
            print(f"Error scraping {title}: {e}")

    if all_jobs_df.empty:
        return []

    # Deduplicate by job_url or id if available
    # JobSpy returns columns: id, site, job_url, job_url_direct, title, company, location, date_posted, etc.
    if "job_url" in all_jobs_df.columns:
        all_jobs_df = all_jobs_df.drop_duplicates(subset=["job_url"])
    
    print(f"Total unique jobs found: {len(all_jobs_df)}")
    
    # Convert to list of dicts and normalize keys for our matcher
    # Matcher expects: job_title, job_description, employer_name, job_city, job_country, job_apply_link, job_posted_at_datetime_utc
    
    normalized_jobs = []
    for _, row in all_jobs_df.iterrows():
        # JobSpy dataframe columns vary slightly but usually include:
        # title, company, location, description, job_url, date_posted
        
        job_dict = {
            "job_title": row.get("title"),
            "job_description": row.get("description"),
            "employer_name": row.get("company"),
            "job_city": row.get("location"), # JobSpy often puts full location string here
            "job_country": "USA", # Implicit
            "job_apply_link": row.get("job_url"),
            "job_posted_at_datetime_utc": str(row.get("date_posted"))
        }
        normalized_jobs.append(job_dict)
        
    return normalized_jobs
