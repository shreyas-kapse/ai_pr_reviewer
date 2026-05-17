from graph.state import ReviewState
from services.reviewers.security_review_service import SecurityReviewService

class SecurityReviewNode:
    
    def __init__(self):
        self.security_review_service = SecurityReviewService()
    
    def security_code_review_node(self, state: ReviewState):
        changed_files = state["changed_files"]
        reviews = []

        for file in changed_files:
            result = self.security_review_service.review_code(file)
            reviews.append(result)

        return {
            "security_reviews": reviews
        }