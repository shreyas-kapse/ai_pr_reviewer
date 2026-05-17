from typing import TypedDict, List, Dict


class ReviewState(TypedDict):

    owner: str
    repo: str
    pr_number: int

    installation_token: str

    changed_files: List[Dict]

    security_reviews: List[Dict]
    performance_reviews: List[Dict]
    bug_risk_reviews: List[Dict]

    final_review: Dict
    github_review: str