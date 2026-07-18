import os
import re
import requests
from django.core.files.base import ContentFile
from accounts.models import Project

def parse_github_url(url):
    """Parse owner and repo name from a GitHub URL."""
    # Normalize URL: strip trailing slash and .git extension
    url = url.strip().rstrip("/")
    if url.endswith(".git"):
        url = url[:-4]

    # Regex to extract owner and repo from standard github urls
    pattern = r"github\.com/([^/]+)/([^/]+)"
    match = re.search(pattern, url)
    if match:
        return match.group(1), match.group(2)
    return None, None

def download_github_repo(project_id):
    """Download a public GitHub repository ZIP archive and save it to the project."""
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return False, "Project not found"

    if not project.github_url:
        return False, "Project does not have a GitHub URL"

    owner, repo = parse_github_url(project.github_url)
    if not owner or not repo:
        project.status = "failed"
        project.save()
        return False, "Invalid GitHub repository URL"

    project.status = "extracting"
    project.save()

    # Try downloading the ZIP ball. We try main first, then master.
    branches = ["main", "master"]
    download_success = False
    response = None

    # Try direct GitHub ZIP URLs first (does not require API key or authentication, has generous limits)
    for branch in branches:
        direct_zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"
        try:
            res = requests.get(direct_zip_url, timeout=30, stream=True)
            if res.status_code == 200:
                response = res
                download_success = True
                break
        except Exception:
            pass

    # If direct heads fail, try standard zipball API endpoint
    if not download_success:
        api_zip_url = f"https://api.github.com/repos/{owner}/{repo}/zipball"
        try:
            res = requests.get(api_zip_url, timeout=30, stream=True)
            if res.status_code == 200:
                response = res
                download_success = True
        except Exception:
            pass

    if not download_success or response is None:
        project.status = "failed"
        project.save()
        return False, f"Failed to download repository '{owner}/{repo}'. Ensure it is public and exists."

    # Save ZIP content to Django FileField
    try:
        zip_filename = f"{owner}_{repo}.zip"
        # Download in chunks to handle larger repos gracefully
        temp_file_content = bytearray()
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                temp_file_content.extend(chunk)

        # Save to Project zip_file Field
        project.zip_file.save(zip_filename, ContentFile(temp_file_content), save=True)
        return True, "Repository downloaded successfully"
    except Exception as e:
        project.status = "failed"
        project.save()
        return False, f"Failed to save downloaded repository: {str(e)}"
