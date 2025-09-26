import requests
from bs4 import BeautifulSoup
import os
import PyPDF2
import git
import glob
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import yt_dlp

DATA_FILE = "data/train.txt"

# List of URLs
URLS = [
    "https://en.wikipedia.org/wiki/Cybersecurity",
    "https://docs.python.org/3/tutorial/index.html",
    "https://0321537114.tiiny.site/",
    "https://pdfhost.io/v/dX6S42GD4V_Programing_full"
]

# List of PDF files
PDFS = []

# List of GitHub repos
REPOS = [
    "https://github.com/psf/requests.git",
    "https://github.com/django/django.git"
]

# List of YouTube videos
YOUTUBE_VIDEOS = [
    "https://www.youtube.com/watch?v=WXsD0ZgxjRw",
]

def fetch_and_clean(url):
    """Download text from a URL and clean it up."""
    print(f"Fetching {url} ...")
    headers = {"User-Agent": "Mozilla/5.0"}  # ✅ Fix for Wikipedia 403
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    paragraphs = soup.find_all("p")
    text = "\n".join([p.get_text() for p in paragraphs])
    return text.strip()

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
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

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
    return text.strip()

def fetch_youtube_transcript(video_url):
    """Fetch transcript of a YouTube video."""
    print(f"Fetching transcript for {video_url} ...")
    video_id = video_url.split("v=")[-1].split("&")[0]

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([t["text"] for t in transcript])
        return text.strip()
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        print(f"No transcript via API: {e}")
    except Exception as e:
        print(f"Transcript API failed: {e}")

    # ✅ Fallback with yt-dlp
    try:
        ydl_opts = {
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["en"],
            "outtmpl": f"data/{video_id}.%(ext)s"
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        sub_file = f"data/{video_id}.en.vtt"
        if os.path.exists(sub_file):
            with open(sub_file, "r", encoding="utf-8") as f:
                return f.read().strip()
    except Exception as e2:
        print(f"No subtitles found: {e2}")

    return ""

def main():
    os.makedirs("data", exist_ok=True)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        # Websites
        for url in URLS:
            try:
                text = fetch_and_clean(url)
                f.write(text + "\n\n")
            except Exception as e:
                print(f"Skipping {url}: {e}")

        # PDFs
        for pdf in PDFS:
            try:
                text = read_pdf(pdf)
                f.write(text + "\n\n")
            except Exception as e:
                print(f"Skipping {pdf}: {e}")

        # GitHub repos
        for repo in REPOS:
            try:
                text = clone_and_extract(repo)
                f.write(text + "\n\n")
            except Exception as e:
                print(f"Skipping {repo}: {e}")

    # YouTube videos
    for video in YOUTUBE_VIDEOS:
        try:
            text = fetch_youtube_transcript(video)
            if text:
                with open(DATA_FILE, "a", encoding="utf-8") as f:
                    f.write(f"\n\n# YOUTUBE VIDEO: {video}\n{text}\n\n")
        except Exception as e:
            print(f"Skipping {video}: {e}")

    print(f"✅ Data saved to {DATA_FILE}")


if __name__ == "__main__":
    main()import requests
from bs4 import BeautifulSoup
import os
import PyPDF2
import git
import glob
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import yt_dlp

DATA_FILE = "data/train.txt"

# List of URLs
URLS = [
    "https://en.wikipedia.org/wiki/Cybersecurity",
    "https://docs.python.org/3/tutorial/index.html",
    "https://0321537114.tiiny.site/"
]

# List of PDF files
PDFS = []

# List of GitHub repos
REPOS = [
    "https://github.com/psf/requests.git",
    "https://github.com/django/django.git"
]

# List of YouTube videos
YOUTUBE_VIDEOS = [
    "https://www.youtube.com/watch?v=WXsD0ZgxjRw",
]

def fetch_and_clean(url):
    """Download text from a URL and clean it up."""
    print(f"Fetching {url} ...")
    headers = {"User-Agent": "Mozilla/5.0"}  # ✅ Fix for Wikipedia 403
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    paragraphs = soup.find_all("p")
    text = "\n".join([p.get_text() for p in paragraphs])
    return text.strip()

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
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

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
    return text.strip()

def fetch_youtube_transcript(video_url):
    """Fetch transcript of a YouTube video."""
    print(f"Fetching transcript for {video_url} ...")
    video_id = video_url.split("v=")[-1].split("&")[0]

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([t["text"] for t in transcript])
        return text.strip()
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        print(f"No transcript via API: {e}")
    except Exception as e:
        print(f"Transcript API failed: {e}")

    # ✅ Fallback with yt-dlp
    try:
        ydl_opts = {
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["en"],
            "outtmpl": f"data/{video_id}.%(ext)s"
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        sub_file = f"data/{video_id}.en.vtt"
        if os.path.exists(sub_file):
            with open(sub_file, "r", encoding="utf-8") as f:
                return f.read().strip()
    except Exception as e2:
        print(f"No subtitles found: {e2}")

    return ""

def main():
    os.makedirs("data", exist_ok=True)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        # Websites
        for url in URLS:
            try:
                text = fetch_and_clean(url)
                f.write(text + "\n\n")
            except Exception as e:
                print(f"Skipping {url}: {e}")

        # PDFs
        for pdf in PDFS:
            try:
                text = read_pdf(pdf)
                f.write(text + "\n\n")
            except Exception as e:
                print(f"Skipping {pdf}: {e}")

        # GitHub repos
        for repo in REPOS:
            try:
                text = clone_and_extract(repo)
                f.write(text + "\n\n")
            except Exception as e:
                print(f"Skipping {repo}: {e}")

    # YouTube videos
    for video in YOUTUBE_VIDEOS:
        try:
            text = fetch_youtube_transcript(video)
            if text:
                with open(DATA_FILE, "a", encoding="utf-8") as f:
                    f.write(f"\n\n# YOUTUBE VIDEO: {video}\n{text}\n\n")
        except Exception as e:
            print(f"Skipping {video}: {e}")

    print(f"✅ Data saved to {DATA_FILE}")


if __name__ == "__main__":
    main()https://en.wikipedia.org/wiki/Cybersecurity
