from services.github_review_service import GitHubReviewService
from graph.state import ReviewState
from langgraph.types import interrupt
from typing import Literal
from langgraph.graph import END
from services.config_service import ConfigService

class PostReviewNode:
    def __init__(self):
        self.github_review_service = GitHubReviewService()
        
    def post_review(self, state:ReviewState):
        response =  self.github_review_service.post_review(
            installation_token=state["installation_token"],
            owner=state["owner"],
            repo=state["repo"],
            pr_number=state["pr_number"],
            review_body=state["github_review"].content
        )
        return response
    
    def approval_router(
        self,
        state: ReviewState
    ):
        if state["approved"]:
            return "post_review"
        return END
    
    def approve_review(
        self,
        state: ReviewState
    ):
        config = ConfigService.get_config()
        print("\n ----------------- PR Review -------------------------")
        print(state["github_review"].content)
        hitl = config["post-review"]["human-in-loop"]
        approved = True

        if hitl:
            approval = input(
                "\nApprove PR review? yes/no: "
            )
            approved = approval.strip().lower() == "yes"

        return {
            "approved": approved
        }