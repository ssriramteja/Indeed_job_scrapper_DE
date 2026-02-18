import pandas as pd
from jobspy import scrape_jobs
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def scrape_single_title(title: str, location: str):
    """
    Worker function to scrape a single title.
    """
    try:
        print(f"Scraping for: {title}")
        jobs: pd.DataFrame = scrape_jobs(
            site_name=["indeed", "zip_recruiter"],
            search_term=title,
            location=location,
            results_wanted=500,
            hours_old=24,
            country_watchlist=["USA"]
        )
        return jobs
    except Exception as e:
        print(f"Error scraping {title}: {e}")
        return pd.DataFrame()

def collect_all_jobs(titles: list, location: str = "United States") -> list:
    """
    Scrapes jobs from Indeed and ZipRecruiter using python-jobspy in parallel.
    Returns a list of dictionaries.
    """
    all_jobs_df = pd.DataFrame()
    
    print(f"Starting parallel scrape for {len(titles)} titles in {location}...")
    
    # Use ThreadPoolExecutor to scrape titles in parallel
    # Max workers set to 5 to avoid overwhelming the sites/rate limits while still being fast
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_title = {executor.submit(scrape_single_title, title, location): title for title in titles}
        
        for future in as_completed(future_to_title):
            title = future_to_title[future]
            try:
                jobs = future.result()
                if not jobs.empty:
                    all_jobs_df = pd.concat([all_jobs_df, jobs], ignore_index=True)
                    print(f"✓ Found {len(jobs)} jobs for {title}")
                else:
                    print(f"- No jobs found for {title}")
            except Exception as e:
                print(f"Exception for {title}: {e}")

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
