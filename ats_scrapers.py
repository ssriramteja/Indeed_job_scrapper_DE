"""
ATS Job Board Scrapers for Workday, Greenhouse, and iCIMS
Uses direct web scraping without requiring API keys.
"""

import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import quote

def search_workday_jobs(title: str, location: str = "United States") -> list:
    """
    Search for jobs on Workday using Google search (free).
    """
    jobs = []
    try:
        # Use Google search to find Workday jobs
        query = f'site:myworkdayjobs.com "{title}" "{location}"'
        url = f"https://www.google.com/search?q={quote(query)}&num=20&tbs=qdr:d"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract job URLs from search results
        for link in soup.find_all('a'):
            href = link.get('href', '')
            if 'myworkdayjobs.com' in href and '/job/' in href:
                # Clean up the URL
                if href.startswith('/url?q='):
                    href = href.split('/url?q=')[1].split('&')[0]
                if href.startswith('http') and href not in [j['job_apply_link'] for j in jobs]:
                    jobs.append({
                        'job_title': title,
                        'employer_name': 'Company (Workday)',
                        'job_apply_link': href,
                        'job_description': f'{title} position',
                        'job_city': location,
                        'job_country': 'USA'
                    })
                    if len(jobs) >= 5:  # Limit to 5 per search
                        break
        
    except Exception as e:
        print(f"  Error searching Workday: {e}")
    
    return jobs

def search_greenhouse_jobs(title: str, location: str = "United States") -> list:
    """
    Search for jobs on Greenhouse using Google search (free).
    """
    jobs = []
    try:
        query = f'site:boards.greenhouse.io "{title}" "{location}"'
        url = f"https://www.google.com/search?q={quote(query)}&num=20&tbs=qdr:d"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        for link in soup.find_all('a'):
            href = link.get('href', '')
            if 'boards.greenhouse.io' in href and '/jobs/' in href:
                if href.startswith('/url?q='):
                    href = href.split('/url?q=')[1].split('&')[0]
                if href.startswith('http') and href not in [j['job_apply_link'] for j in jobs]:
                    jobs.append({
                        'job_title': title,
                        'employer_name': 'Company (Greenhouse)',
                        'job_apply_link': href,
                        'job_description': f'{title} position',
                        'job_city': location,
                        'job_country': 'USA'
                    })
                    if len(jobs) >= 5:
                        break
        
    except Exception as e:
        print(f"  Error searching Greenhouse: {e}")
    
    return jobs

def search_icims_jobs(title: str, location: str = "United States") -> list:
    """
    Search for jobs on iCIMS using Google search (free).
    """
    jobs = []
    try:
        query = f'site:icims.com "{title}" "{location}"'
        url = f"https://www.google.com/search?q={quote(query)}&num=20&tbs=qdr:d"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        for link in soup.find_all('a'):
            href = link.get('href', '')
            if 'icims.com' in href and '/jobs/' in href:
                if href.startswith('/url?q='):
                    href = href.split('/url?q=')[1].split('&')[0]
                if href.startswith('http') and href not in [j['job_apply_link'] for j in jobs]:
                    jobs.append({
                        'job_title': title,
                        'employer_name': 'Company (iCIMS)',
                        'job_apply_link': href,
                        'job_description': f'{title} position',
                        'job_city': location,
                        'job_country': 'USA'
                    })
                    if len(jobs) >= 5:
                        break
        
    except Exception as e:
        print(f"  Error searching iCIMS: {e}")
    
    return jobs

from concurrent.futures import ThreadPoolExecutor, as_completed

def collect_ats_jobs(titles: list, location: str = "United States") -> list:
    """
    Main function to collect jobs from ATS platforms (Workday, Greenhouse, iCIMS).
    Uses ThreadPoolExecutor for parallelized Google searching.
    """
    print("\n" + "=" * 60)
    print("ATS JOB BOARD SCRAPER (Workday, Greenhouse, iCIMS)")
    print("Using parallel Google search for maximum speed!")
    print("=" * 60)
    
    all_jobs = []
    
    # Limit to first 5 titles for ATS to keep search volume reasonable
    search_titles = titles[:5]
    
    def search_worker(platform_func, title, loc):
        platform_name = platform_func.__name__.split('_')[1].capitalize()
        # print(f"  → Searching {platform_name} for {title}...")
        return platform_func(title, loc)

    # We'll run searches for each platform and each title in parallel
    search_tasks = []
    platforms = [search_workday_jobs, search_greenhouse_jobs, search_icims_jobs]
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_info = {}
        for title in search_titles:
            for platform_func in platforms:
                future = executor.submit(search_worker, platform_func, title, location)
                future_to_info[future] = (platform_func.__name__, title)
        
        for future in as_completed(future_to_info):
            func_name, title = future_to_info[future]
            try:
                jobs = future.result()
                if jobs:
                    all_jobs.extend(jobs)
                    platform = func_name.split('_')[1].capitalize()
                    print(f"  ✓ {platform}: Found {len(jobs)} jobs for '{title}'")
            except Exception as e:
                print(f"  ✗ Error in {func_name} for {title}: {e}")
    
    print(f"\n✅ Total ATS jobs found: {len(all_jobs)}")
    return all_jobs

