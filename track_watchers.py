import os
import logging
from github import Github

# Set up logging for better visibility
logging.basicConfig(level=logging.INFO)

# GitHub API Token (retrieved from environment variables)
token = os.getenv('MY_GITHUB_TOKEN')

# Ensure the token is retrieved
if not token:
    logging.error("GitHub token not found. Please set the MY_GITHUB_TOKEN environment variable.")
    exit(1)

# Initialize GitHub API client with token
g = Github(token)

# Function to get all repositories for the authenticated user
def get_repositories():
    user = g.get_user()
    return user.get_repos()

# Function to get watchers of a repository
def get_watchers(repo_name):
    url = f'https://api.github.com/repos/{repo_name}/watchers'
    response = requests.get(url)
    
    if response.status_code != 200:
        logging.error(f"Failed to get watchers for repo {repo_name}. Status code: {response.status_code}")
        return set()  # Return an empty set on failure
    
    return {watcher['login'] for watcher in response.json()}

# Function to send a message to Telegram
def send_telegram_message(message):
    telegram_url = f'https://api.telegram.org/bot{os.getenv("TELEGRAM_BOT_API_TOKEN")}/sendMessage'
    payload = {
        'chat_id': os.getenv('TELEGRAM_CHAT_ID'),
        'text': message
    }
    response = requests.post(telegram_url, data=payload)
    if response.status_code != 200:
        logging.error(f"Failed to send Telegram message. Status code: {response.status_code}")
    else:
        logging.info("Telegram message sent successfully.")

# Function to track new watchers for all repositories
def track_new_watchers():
    all_repos = get_repositories()
    for repo in all_repos:
        repo_name = repo.full_name
        current_watchers = get_watchers(repo_name)

        # Read previously stored watchers (stored in a text file for simplicity)
        watchers_file_path = f"{repo_name}_watchers.txt"
        
        try:
            with open(watchers_file_path, "r") as file:
                stored_watchers = set(file.read().splitlines())
        except FileNotFoundError:
            stored_watchers = set()
        
        # Determine new watchers by comparing
        new_watchers = current_watchers - stored_watchers
        
        if new_watchers:
            for watcher in new_watchers:
                message = f'New watcher: {watcher} started watching your repo: {repo_name}!'
                send_telegram_message(message)

            # Update stored watchers for future comparisons
            with open(watchers_file_path, "w") as file:
                file.write("\n".join(current_watchers))

# Run the function
if __name__ == "__main__":
    track_new_watchers()

