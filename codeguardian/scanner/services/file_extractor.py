import os
import zipfile
import hashlib
from django.conf import settings
from accounts.models import Project, CodeFile

IGNORE_DIRS = {
    ".git",
    "__pycache__",
    "venv",
    "env",
    ".venv",
    ".env",
    "node_modules",
    "migrations",
    ".idea",
    ".vscode",
}

IGNORE_FILES = {
    ".gitignore",
    ".dockerignore",
    "db.sqlite3",
}

def calculate_hash(file_path):
    """Calculate SHA-256 hash of a file to check for changes."""
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256.update(byte_block)
        return sha256.hexdigest()
    except Exception:
        return ""

def count_lines_and_size(file_path):
    """Count lines of code and get file size."""
    try:
        file_size = os.path.getsize(file_path)
        lines = 0
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for _ in f:
                lines += 1
        return lines, file_size
    except Exception:
        return 0, 0

def detect_framework(extracted_dir):
    """Detect if the project is Django, Flask, FastAPI, or generic Python."""
    has_manage_py = False
    has_settings_py = False
    imports_flask = False
    imports_fastapi = False
    imports_django = False

    for root, dirs, files in os.walk(extracted_dir):
        # Prune ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file in files:
            if file == "manage.py":
                has_manage_py = True
            if file == "settings.py":
                has_settings_py = True

            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        if "import flask" in content or "from flask" in content:
                            imports_flask = True
                        if "import fastapi" in content or "from fastapi" in content:
                            imports_fastapi = True
                        if "import django" in content or "from django" in content:
                            imports_django = True
                except Exception:
                    pass

    if has_manage_py or has_settings_py or imports_django:
        return "Django"
    elif imports_fastapi:
        return "FastAPI"
    elif imports_flask:
        return "Flask"
    return "Python"

def extract_and_map_project(project_id):
    """Extract project ZIP, map structure, index files, and detect framework."""
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return False, "Project not found"

    project.status = "extracting"
    project.save()

    # Define extraction directory
    extracted_dir_name = f"project_{project.id}"
    extracted_dir_path = os.path.join(settings.MEDIA_ROOT, "extracted_projects", extracted_dir_name)
    os.makedirs(extracted_dir_path, exist_ok=True)

    project.extracted_path = extracted_dir_path

    python_files_count = 0
    total_files_count = 0

    if project.upload_type == "zip":
        if not project.zip_file:
            project.status = "failed"
            project.save()
            return False, "No zip file associated with this project"

        zip_path = project.zip_file.path
        if not os.path.exists(zip_path):
            project.status = "failed"
            project.save()
            return False, f"ZIP file not found on disk at {zip_path}"

        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Security: prevent zip slip vulnerability
                for member in zip_ref.infolist():
                    filename = member.filename
                    # Resolve to absolute path to verify it is within the target directory
                    target_path = os.path.abspath(os.path.join(extracted_dir_path, filename))
                    if not target_path.startswith(os.path.abspath(extracted_dir_path)):
                        return False, "Unsafe ZIP file (directory traversal attempt)"

                zip_ref.extractall(extracted_dir_path)
        except zipfile.BadZipFile:
            project.status = "failed"
            project.save()
            return False, "Invalid or corrupted ZIP archive"
        except Exception as e:
            project.status = "failed"
            project.save()
            return False, f"Failed to extract ZIP: {str(e)}"

    elif project.upload_type == "single_file":
        if not project.zip_file:
            project.status = "failed"
            project.save()
            return False, "No file uploaded"

        file_path = project.zip_file.path
        if not os.path.exists(file_path):
            project.status = "failed"
            project.save()
            return False, "Uploaded file not found on disk"

        # Copy single file into the extracted directory
        filename = os.path.basename(file_path)
        target_path = os.path.join(extracted_dir_path, filename)
        try:
            with open(file_path, "rb") as src, open(target_path, "wb") as dst:
                dst.write(src.read())
        except Exception as e:
            project.status = "failed"
            project.save()
            return False, f"Failed to copy uploaded file: {str(e)}"

    # Clear out any existing CodeFile records for this project (in case of re-extracting)
    CodeFile.objects.filter(project=project).delete()

    # Index files
    for root, dirs, files in os.walk(extracted_dir_path):
        # Prune ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file in files:
            if file in IGNORE_FILES:
                continue

            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, extracted_dir_path)
            _, ext = os.path.splitext(file)

            total_files_count += 1
            is_py = ext.lower() == ".py"

            if is_py:
                python_files_count += 1
                lines, size = count_lines_and_size(file_path)
                file_hash = calculate_hash(file_path)

                CodeFile.objects.create(
                    project=project,
                    file_name=file,
                    file_path=relative_path,
                    extension=ext,
                    lines_of_code=lines,
                    file_size=size,
                    content_hash=file_hash
                )
            else:
                # Index non-python files too, but LoC = 0
                file_size = os.path.getsize(file_path)
                CodeFile.objects.create(
                    project=project,
                    file_name=file,
                    file_path=relative_path,
                    extension=ext,
                    lines_of_code=0,
                    file_size=file_size,
                    content_hash=""
                )

    # Detect project type / framework
    framework = detect_framework(extracted_dir_path)

    project.status = "ready"
    project.language = f"Python ({framework})"
    project.total_files = total_files_count
    project.total_python_files = python_files_count
    project.save()

    return True, "Project extracted and indexed successfully"
