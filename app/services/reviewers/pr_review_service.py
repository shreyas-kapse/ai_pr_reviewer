from services.prompts.pr_review_prompt import final_review_prompt
from services.schema.review_schema import FinalReviewSchema
from services.reviewers.base_reviewer import BaseReviewer
from services.llm_service import LLMService
from langchain_core.prompts import PromptTemplate

class PRReviewService:
    def __init__(self):
        self.llm = LLMService.get_llm()
        self.llm = self.llm.with_structured_output(FinalReviewSchema)
    
    def review_code(self, 
                    file_patch: str, 
                    security_review:list, 
                    bug_risk_review:list,
                    performance_review:list):
        
        prompt = PromptTemplate(
            template=final_review_prompt,
            input_variables=["file_patch", "security_review", "performance_review", "bug_risk_review"]
        )
        response = self.llm.invoke(
            prompt.format(
            file_patch=file_patch,
            security_review = security_review,
            performance_review= performance_review,
            bug_risk_review = bug_risk_review
        ))
        
        return response