import requests

class GitHubReviewService:

    def post_review(
        self,
        installation_token: str,
        owner: str,
        repo: str,
        pr_number: int,
        review_body: str
    ):

        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews"

        headers = {
            "Authorization": f"Bearer {installation_token}",
            "Accept": "application/vnd.github+json"
        }
        payload = {
            "body": review_body,
            "event": "COMMENT"
        }
        response = requests.post(
            url,
            headers=headers,
            json=payload
        )
        print("\n========== GITHUB REVIEW RESPONSE ==========")
        print(response.status_code)
        print(response.text)

        response.raise_for_status()
        return response.json()