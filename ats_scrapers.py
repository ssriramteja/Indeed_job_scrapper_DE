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

def collect_ats_jobs(titles: list, location: str = "United States") -> list:
    """
    Main function to collect jobs from ATS platforms (Workday, Greenhouse, iCIMS).
    Uses free Google search - no API key required!
    """
    print("\n" + "=" * 60)
    print("ATS JOB BOARD SCRAPER (Workday, Greenhouse, iCIMS)")
    print("Using free Google search - no API key needed!")
    print("=" * 60)
    
    all_jobs = []
    
    # Limit to first 3 titles to avoid too many requests
    search_titles = titles[:3]
    
    for idx, title in enumerate(search_titles):
        print(f"\n[{idx+1}/{len(search_titles)}] Searching for: {title}")
        
        # Search each platform
        print("  → Workday...", end=" ")
        workday_jobs = search_workday_jobs(title, location)
        print(f"found {len(workday_jobs)}")
        all_jobs.extend(workday_jobs)
        time.sleep(2)  # Rate limiting
        
        print("  → Greenhouse...", end=" ")
        greenhouse_jobs = search_greenhouse_jobs(title, location)
        print(f"found {len(greenhouse_jobs)}")
        all_jobs.extend(greenhouse_jobs)
        time.sleep(2)
        
        print("  → iCIMS...", end=" ")
        icims_jobs = search_icims_jobs(title, location)
        print(f"found {len(icims_jobs)}")
        all_jobs.extend(icims_jobs)
        time.sleep(2)
    
    print(f"\n✅ Total ATS jobs found: {len(all_jobs)}")
    return all_jobs

