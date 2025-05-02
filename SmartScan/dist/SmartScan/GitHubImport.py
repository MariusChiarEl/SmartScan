import github
import subprocess
import os

class GitHubImport():

    def __init__(self, repo_path, gitHub_token):
        # GitHub API token (for authentication)
        # Necesarry when working with private repos
        self.GITHUB_TOKEN = gitHub_token # "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"

        # Repository details
        self.REPO_PATH = repo_path # "https://github.com/MariusChiarEl/Blockchain-project.git"

        self.clone_repo()

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
        except subprocess.CalledProcessError as e:
            print(f"Failed to clone repository: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
