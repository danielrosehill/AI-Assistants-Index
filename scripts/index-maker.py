import os
import re
import requests
from pathlib import Path

# Constants
REPO_LIST_FILE = "repolist.txt"
README_FILE = "README.md"
MEMORY_FILE = ".repo_memory"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/analyze"  # Example API endpoint
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")  # API key from environment or GitHub secrets

def find_repo_base():
    """Recursively search for the repository base directory."""
    current_dir = Path(os.getcwd())
    while not (current_dir / REPO_LIST_FILE).exists():
        if current_dir.parent == current_dir:
            raise FileNotFoundError("Repository base not found.")
        current_dir = current_dir.parent
    return current_dir

def read_repolist(repo_base):
    """Read and parse the repolist.txt file."""
    repolist_path = repo_base / REPO_LIST_FILE
    with open(repolist_path, "r") as file:
        urls = file.read().splitlines()
    return [url.strip() for url in urls if url.strip()]

def fetch_repo_info(url):
    """Fetch repository title and description using Deepseek's API."""
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
    payload = {"url": url}
    response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        return data.get("title", "Untitled"), data.get("description", "No description available.")
    else:
        return "Untitled", "No description available."

def update_readme(repo_base, repo_data):
    """Update the README.md file with the repository list."""
    readme_path = repo_base / README_FILE
    with open(readme_path, "w") as file:
        file.write("# Repository Index\n\n")
        for title, url, description in sorted(repo_data, key=lambda x: x[0].lower()):
            file.write(f"# {title}\n\n")
            file.write(f"[![Visit Repo](https://img.shields.io/badge/Visit-Repo-blue?style=for-the-badge&logo=github)]({url})\n\n")
            file.write(f"{description}\n\n")

def main():
    try:
        repo_base = find_repo_base()
        urls = read_repolist(repo_base)
        
        # Load previously stored repositories to avoid duplicates
        memory_path = repo_base / MEMORY_FILE
        if memory_path.exists():
            with open(memory_path, "r") as file:
                stored_repos = set(file.read().splitlines())
        else:
            stored_repos = set()

        repo_data = []
        for url in urls:
            if url not in stored_repos:
                title, description = fetch_repo_info(url)
                repo_data.append((title, url, description))
                stored_repos.add(url)

        # Update README and memory file
        update_readme(repo_base, repo_data)
        with open(memory_path, "w") as file:
            file.write("\n".join(stored_repos))

        print("README.md updated successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()