from graph.state import ReviewState
from services.reviewers.final_review_service import FinalReviewService

class FinalReviewNode:
    def __init__(self):
        self.final_review_service = FinalReviewService()
    
    def final_code_review_node(self, state: ReviewState):
        result = self.final_review_service.review_code(
            review = state['final_review']
        )

        return {
            "github_review": result
        }
    