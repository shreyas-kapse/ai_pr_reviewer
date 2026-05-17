from graph.state import ReviewState
from services.reviewers.performance_review_service import PerformanceReviewService

class PerformanceReviewNode:
    
    def __init__(self):
        self.performance_review_service = PerformanceReviewService()
    
    async def performance_code_review_node(self, state: ReviewState):
        changed_files = state["changed_files"]
        reviews = []

        for file in changed_files:
            result = await self.performance_review_service.review_code(file)
            reviews.append(result)

        return {
            "performance_reviews": reviews
        }