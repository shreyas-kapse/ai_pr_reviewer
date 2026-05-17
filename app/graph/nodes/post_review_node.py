from services.github_review_service import GitHubReviewService
from graph.state import ReviewState
class PostReviewNode:
    def __init__(self):
        self.github_review_service = GitHubReviewService()
        
    def post_review(self, state:ReviewState):
        print(type(state["github_review"]))
        response = self.github_review_service.post_review(
            installation_token=state["installation_token"],
            owner=state["owner"],
            repo=state["repo"],
            pr_number=state["pr_number"],
            review_body=state["github_review"].content
        )
        return response