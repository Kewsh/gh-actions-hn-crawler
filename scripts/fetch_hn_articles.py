#!/usr/bin/env python3
"""
Fetch top 20 articles from Hacker News and save them as offline-readable HTML files.
"""

import os
import re
import json
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup


HN_API_URL = "https://hacker-news.firebaseio.com/v0"
ARTICLES_DIR = Path("articles")
MAX_ARTICLES = 20
TIMEOUT = 30


def sanitize_filename(filename):
    """Sanitize filename to be filesystem-safe."""
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    return filename.strip()


def fetch_top_stories():
    """Fetch top story IDs from HN API."""
    print("Fetching top stories from Hacker News...")
    response = requests.get(f"{HN_API_URL}/topstories.json", timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()[:MAX_ARTICLES]


def fetch_story_details(story_id):
    """Fetch story details from HN API."""
    response = requests.get(f"{HN_API_URL}/item/{story_id}.json", timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()


def download_article(url, title, rank):
    """Download article and save as self-contained HTML."""
    print(f"  [{rank}] Downloading: {title}")
    print(f"      URL: {url}")
    
    try:
        # Fetch the article
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, timeout=TIMEOUT, headers=headers, allow_redirects=True)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html5lib')
        
        # Try to inline images as base64 (optional, for better offline experience)
        for img in soup.find_all('img'):
            img_url = img.get('src')
            if img_url:
                try:
                    # Make absolute URL
                    img_url = urljoin(url, img_url)
                    img_response = requests.get(img_url, timeout=10, headers=headers)
                    if img_response.status_code == 200:
                        import base64
                        content_type = img_response.headers.get('content-type', 'image/jpeg')
                        img_data = base64.b64encode(img_response.content).decode('utf-8')
                        img['src'] = f"data:{content_type};base64,{img_data}"
                except Exception as e:
                    print(f"      Warning: Could not inline image {img_url}: {e}")
        
        # Add metadata header
        metadata_html = f"""
        <div style="background: #ff6600; color: white; padding: 20px; margin-bottom: 20px; font-family: sans-serif;">
            <h1 style="margin: 0 0 10px 0;">#{rank} - {title}</h1>
            <p style="margin: 5px 0;"><strong>Original URL:</strong> <a href="{url}" style="color: white;">{url}</a></p>
            <p style="margin: 5px 0;"><strong>Downloaded:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            <p style="margin: 5px 0;"><strong>Source:</strong> Hacker News Top Stories</p>
        </div>
        """
        
        if soup.body:
            soup.body.insert(0, BeautifulSoup(metadata_html, 'html.parser'))
        
        # Create filename
        domain = urlparse(url).netloc
        safe_title = sanitize_filename(title)
        filename = f"{rank:02d}_{safe_title}_{domain}.html"
        filepath = ARTICLES_DIR / filename
        
        # Save HTML
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        
        print(f"      ✓ Saved to: {filename}")
        return {
            'rank': rank,
            'title': title,
            'url': url,
            'filename': filename,
            'success': True
        }
        
    except Exception as e:
        print(f"      ✗ Error downloading article: {e}")
        return {
            'rank': rank,
            'title': title,
            'url': url,
            'error': str(e),
            'success': False
        }


def main():
    """Main function to fetch and save HN articles."""
    print("=" * 80)
    print("Hacker News Article Fetcher")
    print("=" * 80)
    
    # Create articles directory
    ARTICLES_DIR.mkdir(exist_ok=True)
    
    # Fetch top stories
    story_ids = fetch_top_stories()
    print(f"Found {len(story_ids)} top stories\n")
    
    results = []
    
    # Process each story
    for i, story_id in enumerate(story_ids, 1):
        try:
            story = fetch_story_details(story_id)
            
            # Skip stories without URLs (Ask HN, Show HN without links, etc.)
            if 'url' not in story:
                print(f"  [{i}] Skipping: {story.get('title', 'No title')} (no URL)")
                results.append({
                    'rank': i,
                    'title': story.get('title', 'No title'),
                    'url': None,
                    'success': False,
                    'error': 'No URL'
                })
                continue
            
            title = story.get('title', 'Untitled')
            url = story['url']
            
            result = download_article(url, title, i)
            results.append(result)
            
            # Be nice to servers
            time.sleep(1)
            
        except Exception as e:
            print(f"  [{i}] Error processing story {story_id}: {e}")
            results.append({
                'rank': i,
                'title': 'Error',
                'url': None,
                'success': False,
                'error': str(e)
            })
    
    # Save metadata
    metadata = {
        'fetched_at': datetime.now().isoformat(),
        'total_articles': len(story_ids),
        'successful_downloads': sum(1 for r in results if r['success']),
        'articles': results
    }
    
    with open(ARTICLES_DIR / 'metadata.json', 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    
    # Create index.html
    create_index(results)
    
    # Print summary
    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)
    successful = sum(1 for r in results if r['success'])
    print(f"Total articles: {len(results)}")
    print(f"Successfully downloaded: {successful}")
    print(f"Failed: {len(results) - successful}")
    print(f"\nArticles saved to: {ARTICLES_DIR.absolute()}")
    print("=" * 80)


def create_index(results):
    """Create an index.html file listing all articles."""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hacker News Top 20 Articles</title>
    <style>
        body {
            font-family: Verdana, Geneva, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f6f6ef;
        }
        h1 {
            color: #ff6600;
            border-bottom: 2px solid #ff6600;
            padding-bottom: 10px;
        }
        .article {
            background: white;
            margin: 15px 0;
            padding: 15px;
            border-left: 4px solid #ff6600;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .article.failed {
            border-left-color: #ccc;
            opacity: 0.6;
        }
        .rank {
            font-weight: bold;
            color: #ff6600;
            font-size: 1.2em;
            margin-right: 10px;
        }
        .title {
            font-size: 1.1em;
            color: #000;
            text-decoration: none;
        }
        .title:hover {
            text-decoration: underline;
        }
        .url {
            color: #828282;
            font-size: 0.9em;
            margin-top: 5px;
        }
        .error {
            color: #d00;
            font-size: 0.9em;
            margin-top: 5px;
        }
        .meta {
            color: #828282;
            font-size: 0.9em;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #ccc;
        }
    </style>
</head>
<body>
    <h1>🔥 Hacker News Top 20 Articles</h1>
    <p class="meta">Downloaded: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC') + """</p>
    
    <div class="articles">
"""
    
    for result in results:
        if result['success']:
            html += f"""
        <div class="article">
            <span class="rank">#{result['rank']}</span>
            <a href="{result['filename']}" class="title">{result['title']}</a>
            <div class="url">Original: <a href="{result['url']}" target="_blank">{result['url']}</a></div>
        </div>
"""
        else:
            html += f"""
        <div class="article failed">
            <span class="rank">#{result['rank']}</span>
            <span class="title">{result['title']}</span>
            <div class="error">Failed to download: {result.get('error', 'Unknown error')}</div>
            {f'<div class="url">URL: {result["url"]}</div>' if result.get('url') else ''}
        </div>
"""
    
    html += """
    </div>
    
    <div class="meta">
        <p><strong>Note:</strong> These articles were downloaded from Hacker News top stories and saved for offline reading.</p>
        <p>Click on any article title to read it offline. Original URLs are preserved for reference.</p>
    </div>
</body>
</html>
"""
    
    with open(ARTICLES_DIR / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n  ✓ Created index.html")


if __name__ == '__main__':
    main()
