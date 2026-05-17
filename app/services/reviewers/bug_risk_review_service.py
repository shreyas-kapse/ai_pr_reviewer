from services.prompts.bug_risk_prompt import bug_risk_prompt
from services.schema.review_schema import ReviewSchema
from services.reviewers.base_reviewer import BaseReviewer
from services.llm_service import LLMService
from langchain_core.prompts import PromptTemplate

class BugRiskReviewService(BaseReviewer):
    def __init__(self):
        self.llm = LLMService.get_llm()
        self.llm = self.llm.with_structured_output(ReviewSchema)
    
    async def review_code(self, file_patch: list):
        prompt = PromptTemplate(
            template=bug_risk_prompt,
            input_variables=["file_patch"]
        )
        response = await self.llm.ainvoke(prompt.format(
            file_patch=file_patch
        ))
        
        return response