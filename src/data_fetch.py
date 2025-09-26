import requests
from bs4 import BeautifulSoup
import os
import PyPDF2
import git
import glob
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp

DATA_FILE = "data/train.txt"

# List of URLs
URLS = [
    "https://en.wikipedia.org/wiki/Cybersecurity",
    "https://docs.python.org/3/tutorial/index.html",
    "https://0321537114.tiiny.site/"  # dead link, will be skipped gracefully
]

# List of PDF files
PDFS = [
    # "data/sample.pdf",
    # "https://example.com/ebook.pdf"
]

# List of GitHub repos
REPOS = [
    "https://github.com/psf/requests.git",   # Python requests library
    "https://github.com/django/django.git"   # Django framework
]

# List of YouTube videos
YOUTUBE_VIDEOS = [
    "https://www.youtube.com/watch?v=WXsD0ZgxjRw",  # Example: Python tutorial
]

def fetch_and_clean(url):
    """Download text from a URL and clean it up."""
    print(f"Fetching {url} ...")
    headers = {"User-Agent": "Mozilla/5.0"}  # Spoof browser to avoid 403
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    paragraphs = soup.find_all("p")
    text = "\n".join([p.get_text() for p in paragraphs])
    return text

def read_pdf(pdf_path):
    """Extract text from a PDF file."""
    print(f"Reading PDF: {pdf_path}")
    text = ""
    if pdf_path.startswith("http"):
        r = requests.get(pdf_path, timeout=10)
        pdf_path = "data/temp.pdf"
        with open(pdf_path, "wb") as f:
            f.write(r.content)

    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def clone_and_extract(repo_url):
    """Clone a repo and read code/docs into text."""
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    repo_path = os.path.join("data", repo_name)

    if not os.path.exists(repo_path):
        print(f"Cloning {repo_url} ...")
        git.Repo.clone_from(repo_url, repo_path)

    text = ""
    for ext in ["py", "md", "txt", "js"]:
        for file in glob.glob(f"{repo_path}/**/*.{ext}", recursive=True):
            try:
                with open(file, "r", encoding="utf-8", errors="ignore") as f:
                    text += f"\n\n# FILE: {file}\n" + f.read()
            except Exception as e:
                print(f"Skipping {file}: {e}")
    return text

def fetch_youtube_transcript(video_url):
    """Fetch transcript of a YouTube video."""
    print(f"Fetching transcript for {video_url} ...")
    video_id = video_url.split("v=")[-1].split("&")[0]

    try:
        # Works with upgraded youtube-transcript-api
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([t["text"] for t in transcript])
        return text
    except Exception as e:
        print(f"No transcript API for {video_url}: {e}")

        try:
            ydl_opts = {
                "skip_download": True,
                "writesubtitles": True,
                "writeautomaticsub": True,
                "subtitleslangs": ["en"],
                "outtmpl": "data/%(id)s.%(ext)s"
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])

            sub_file = f"data/{video_id}.en.vtt"
            if os.path.exists(sub_file):
                with open(sub_file, "r", encoding="utf-8") as f:
                    text = f.read()
                return text
        except Exception as e2:
            print(f"No subtitles found: {e2}")

    return ""

def main():
    os.makedirs("data", exist_ok=True)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        # From websites
        for url in URLS:
            try:
                text = fetch_and_clean(url)
                f.write(f"\n\n# WEBSITE: {url}\n{text}\n\n")
            except Exception as e:
                print(f"Failed {url}: {e}")

        # From PDFs
        for pdf in PDFS:
            try:
                text = read_pdf(pdf)
                f.write(f"\n\n# PDF: {pdf}\n{text}\n\n")
            except Exception as e:
                print(f"Failed {pdf}: {e}")

        # From GitHub repos
        for repo in REPOS:
            try:
                text = clone_and_extract(repo)
                f.write(f"\n\n# REPO: {repo}\n{text}\n\n")
            except Exception as e:
                print(f"Failed {repo}: {e}")

    # From YouTube videos (append mode)
    for video in YOUTUBE_VIDEOS:
        try:
            text = fetch_youtube_transcript(video)
            if text.strip():
                with open(DATA_FILE, "a", encoding="utf-8") as f:
                    f.write(f"\n\n# YOUTUBE VIDEO: {video}\n{text}\n\n")
        except Exception as e:
            print(f"Failed {video}: {e}")

    print(f"✅ Data saved to {DATA_FILE}")


if __name__ == "__main__":
    main()to
