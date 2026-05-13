from services.prompts.security_prompt import security_review_prompt
from services.schema.review_schema import ReviewSchema
from services.reviewers.base_reviewer import BaseReviewer
from services.llm_service import LLMService
from langchain_core.prompts import PromptTemplate

class SecurityReviewService(BaseReviewer):
    def __init__(self):
        self.llm = LLMService.get_llm()
        self.llm = self.llm.with_structured_output(ReviewSchema)
    
    def review_code(self, file_patch: list):
        prompt = PromptTemplate(
            template=security_review_prompt,
            input_variables=["file_patch"]
        )
        response = self.llm.invoke(prompt.format(
            file_patch=file_patch
        ))
        
        return response