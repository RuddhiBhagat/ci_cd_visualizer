import os
import requests

GITHUB_API_URL = "https://api.github.com"

def get_headers():
    return {
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
        "Accept": "application/vnd.github+json"
    }

def get_workflows():
    print("\n [DEBUG] get_workflows() called")

    owner = os.getenv("REPO_OWNER")
    repo = os.getenv("REPO_NAME")
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/actions/workflows"

    print(f"Requesting workflows for: {owner}/{repo}")
    print("Request URL:", url)
    print("Headers:", get_headers())

    response = requests.get(url, headers=get_headers())

    print(" Response Status:", response.status_code)
    print("Response Body:", response.text)

    if response.status_code == 200:
        return response.json().get("workflows", [])
    else:
        print("Failed to fetch workflows")
        return []

def trigger_workflow(workflow_id, ref="main"):
    print(f"\n[DEBUG] trigger_workflow({workflow_id}) called")

    owner = os.getenv("REPO_OWNER")
    repo = os.getenv("REPO_NAME")
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches"

    data = {"ref": ref}
    print("POST URL:", url)
    print("Payload:", data)

    response = requests.post(url, headers=get_headers(), json=data)

    print("Response Status:", response.status_code)
    print("Response Body:", response.text)

    if response.status_code == 204:
        print("Workflow triggered successfully")
        return True
    else:
        print("Trigger failed:", response.status_code, response.text)  # <== this line matters
        return False



def get_workflow_runs():
    print("\n[DEBUG] get_workflow_runs() called")

    owner = os.getenv("REPO_OWNER")
    repo = os.getenv("REPO_NAME")
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/actions/runs"

    response = requests.get(url, headers=get_headers())

    print("URL:", url)
    print("Status:", response.status_code)
    print("Body:", response.text[:500])

    if response.status_code == 200:
        return response.json().get("workflow_runs", [])
    else:
        print("Failed to fetch workflow runs")
        return []

def get_user_repositories():
    print("\n[DEBUG] get_user_repositories() called")

    # Get your username
    user_resp = requests.get(f"{GITHUB_API_URL}/user", headers=get_headers())
    if user_resp.status_code != 200:
        print("Failed to fetch user profile")
        return []

    current_user = user_resp.json().get("login")
    print(f"[DEBUG] Logged-in GitHub user: {current_user}")

    # Fetch all repos (max 100)
    repo_resp = requests.get(f"{GITHUB_API_URL}/user/repos?per_page=100", headers=get_headers())
    if repo_resp.status_code != 200:
        print("Failed to fetch repositories:", repo_resp.status_code)
        return []

    repos = repo_resp.json()

    # Print log to debug owner vs current user
    for repo in repos:
        print(f"REPO OWNER: {repo['owner']['login']} — CURRENT USER: {current_user}")

    # Only your repos
    owned_repos = [
        {
            "name": repo["name"],
            "full_name": repo["full_name"]
        }
        for repo in repos
        if repo["owner"]["login"] == current_user
    ]

    print(f"[DEBUG] Total owned repos: {len(owned_repos)}")
    return owned_repos
