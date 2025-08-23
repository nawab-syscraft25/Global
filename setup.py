import os

# Project structure
structure = {
    "app": [
        "__init__.py",
        "main.py",
        "config.py",
        "models/__init__.py",
        "schemas/__init__.py",
        "crud/__init__.py",
        "routes/__init__.py",
        "services/__init__.py",
        "utils/__init__.py",
        "auth/__init__.py",
    ],
    "tests": [
        "__init__.py",
        "test_main.py"
    ],
    "alembic": [],  # migration folder
}

def create_structure(base_path="."):
    for folder, files in structure.items():
        folder_path = os.path.join(base_path, folder)
        os.makedirs(folder_path, exist_ok=True)

        for file in files:
            file_path = os.path.join(folder_path, file)

            # Create subfolders if file path has nested dirs
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            if not os.path.exists(file_path):
                with open(file_path, "w") as f:
                    f.write("")

    # Root-level files
    root_files = [
        ".env",
        ".gitignore",
        "requirements.txt",
        "alembic.ini",
        "README.md"
    ]
    for file in root_files:
        path = os.path.join(base_path, file)
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write("")

if __name__ == "__main__":
    create_structure()
    print("✅ FastAPI project structure created successfully!")
