 # Hacker News Article Crawler
 
 A GitHub Actions workflow that fetches the top 20 articles from Hacker News and saves them as offline-readable HTML files.
 
 ## How It Works
 
 When you manually trigger the workflow:
 1. Fetches the top 20 stories from Hacker News API
 2. Downloads each article's webpage
 3. Converts them to self-contained HTML files with embedded images
 4. Creates an index page for easy navigation
 5. Commits everything to the repository
 
 ## Usage
 
 ### Running the Workflow
 
 1. Go to the **Actions** tab in your GitHub repository
 2. Click on **"Fetch HN Top Articles"** workflow
 3. Click **"Run workflow"** button
 4. Select the branch (usually `main`)
 5. Click **"Run workflow"**
 
 The workflow will take a few minutes to complete.
 
 ### Reading Articles Offline
 
 After the workflow completes:
 
 1. Pull the latest changes:
    ```bash
    git pull
    ```
 
 2. Open the index page in your browser:
    ```bash
    open articles/index.html
    # or on Linux:
    xdg-open articles/index.html
    # or on Windows:
    start articles/index.html
    ```
 
 3. Click on any article to read it offline!
 
 All articles are saved in the `articles/` directory with:
 - Full HTML content
 - Embedded images (when possible)
 - Metadata header showing title, URL, and download date
 - Original formatting preserved
 
 ## File Structure
 
 ```
 .
 ├── .github/
 │   └── workflows/
 │       └── fetch-hn-articles.yml    # GitHub Actions workflow
 ├── scripts/
 │   └── fetch_hn_articles.py         # Python scraper script
 ├── articles/                         # Downloaded articles (created by workflow)
 │   ├── index.html                   # Navigation page
 │   ├── metadata.json                # Download metadata
 │   └── *.html                       # Individual articles
 └── README.md
 ```
 
 ## Features
 
 - ✅ Fetches top 20 HN articles
 - ✅ Saves as self-contained HTML files
 - ✅ Embeds images for offline viewing
 - ✅ Creates beautiful index page
 - ✅ Preserves original URLs
 - ✅ Adds metadata headers
 - ✅ Handles errors gracefully
 - ✅ Manual trigger only (no automatic runs)
 
 ## Requirements
 
 - GitHub repository with Actions enabled
 - No local setup required (runs entirely in GitHub Actions)
 
 ## Notes
 
 - Some websites may block automated downloads
 - Articles without URLs (Ask HN, Show HN text posts) are skipped
 - Images are embedded when possible, but some may fail to load
 - Each run overwrites previous articles in the `articles/` directory
 
 ## Troubleshooting
 
 If the workflow fails:
 1. Check the Actions tab for error logs
 2. Some websites may block the scraper
 3. Network timeouts may occur for slow sites
 
 The workflow will continue even if some articles fail to download.
