from services.prompts.final_github_review_prompt import FINAL_GITHUB_REVIEW_PROMPT
from services.schema.review_schema import FinalReviewSchema
from services.reviewers.base_reviewer import BaseReviewer
from services.llm_service import LLMService
from langchain_core.prompts import PromptTemplate

class FinalReviewService(BaseReviewer):
    def __init__(self):
        self.llm = LLMService.get_llm()
    
    def review_code(self, review: FinalReviewSchema):
        prompt = PromptTemplate(
            template=FINAL_GITHUB_REVIEW_PROMPT,
            input_variables=["final_review"]
        )
        response = self.llm.invoke(prompt.format(
            final_review=review
        ))
        return response