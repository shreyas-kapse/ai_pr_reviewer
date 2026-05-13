from pydantic import BaseModel
from typing import List, Literal, Optional


class ReviewSchema(BaseModel):
    review_type: str
    severity: str
    file_name: str
    line_number: Optional[int]
    issue: str
    suggestion: str

class FinalReviewSchema(BaseModel):
    overall_severity: Literal["low", "medium", "high"]
    merge_recommendation: Literal[
        "approve",
        "changes_requested",
        "needs_further_review"
    ]
    summary: str
    top_issues: List[ReviewSchema]