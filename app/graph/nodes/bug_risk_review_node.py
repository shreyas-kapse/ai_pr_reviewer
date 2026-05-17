from graph.state import ReviewState
from services.reviewers.bug_risk_review_service import BugRiskReviewService

class BugRiskReviewNode:
    
    def __init__(self):
        self.bug_risk_review_service = BugRiskReviewService()
    
    def bug_risk_code_review_node(self, state: ReviewState):
        changed_files = state["changed_files"]
        reviews = []

        for file in changed_files:
            result = self.bug_risk_review_service.review_code(file)
            reviews.append(result)

        return {
            "bug_risk_reviews": reviews
        }