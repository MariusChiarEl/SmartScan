from genericpath import exists
import github
import subprocess
import os

class GitHubImport():

    def __init__(self, repo_path):
        # GitHub API token (for authentication)
        # Necesarry when working with private repos

        api_key_path = os.path.join(os.getcwd(), "API_KEY.txt")
        exists = os.path.isfile(api_key_path)
        if not exists:
            print("API key file not found. Please create a file named 'API_KEY.txt' in the current directory and enter the API Key there.")
        else:
            with open(api_key_path, "r", encoding="utf-8") as api_key_file:
                api_key = api_key_file.read()
                self.GITHUB_TOKEN = api_key # "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"

        # Repository details
        self.REPO_PATH = repo_path # "https://github.com/MariusChiarEl/Blockchain-project.git"

        self.clone_result = self.clone_repo()

    def clone_repo(self):
        git_hub = github.Github()

        # remove cloned repo if already exists
        clone_dir = os.path.join(os.getcwd(), "ClonedRepo")
        if os.path.exists(clone_dir):
            os.system('rmdir /S /Q "{}"'.format(clone_dir))

        os.mkdir(path=clone_dir)

        # Directory to clone the repository into
        clone_dir = os.path.join(clone_dir)

        # Clone the repository using git command
        try:
            subprocess.run(["git", "clone", self.REPO_PATH, clone_dir], check=True)
            print("Repository cloned successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to clone repository: {e}")
            return False
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
