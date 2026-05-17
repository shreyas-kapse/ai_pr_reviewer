from graph.state import ReviewState
from services.reviewers.pr_review_service import PRReviewService

class PRReviewNode:
    def __init__(self):
        self.pr_review_service = PRReviewService()
    
    def pr_code_review_node(self, state: ReviewState):
        result = self.pr_review_service.review_code(
        file_patch=state["changed_files"],
        security_review=state["security_reviews"],
        performance_review=state["performance_reviews"],
        bug_risk_review=state["bug_risk_reviews"]
        )

        return {
            "final_review": result
        }
    