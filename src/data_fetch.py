import requests
from bs4 import BeautifulSoup
import os
import PyPDF2
import git
import glob

DATA_FILE = "data/train.txt"

# List of URLs
URLS = [
    "https://en.wikipedia.org/wiki/Cybersecurity",
    "https://docs.python.org/3/tutorial/index.html"
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

def fetch_and_clean(url):
    """Download text from a URL and clean it up."""
    print(f"Fetching {url} ...")
    response = requests.get(url, timeout=10)
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
    # Collect .py, .md, .txt, .js files
    for ext in ["py", "md", "txt", "js"]:
        for file in glob.glob(f"{repo_path}/**/*.{ext}", recursive=True):
            try:
                with open(file, "r", encoding="utf-8", errors="ignore") as f:
                    text += f"\n\n# FILE: {file}\n" + f.read()
            except Exception as e:
                print(f"Skipping {file}: {e}")
    return text

def main():
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        # From websites
        for url in URLS:
            try:
                text = fetch_and_clean(url)
                f.write(text + "\n\n")
            except Exception as e:
                print(f"Failed {url}: {e}")

        # From PDFs
        for pdf in PDFS:
            try:
                text = read_pdf(pdf)
                f.write(text + "\n\n")
            except Exception as e:
                print(f"Failed {pdf}: {e}")

        # From GitHub repos
        for repo in REPOS:
            try:
                text = clone_and_extract(repo)
                f.write(text + "\n\n")
            except Exception as e:
                print(f"Failed {repo}: {e}")

    print(f"✅ Data saved to {DATA_FILE}")

if __name__ == "__main__":
    main()
