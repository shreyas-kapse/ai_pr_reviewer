from langgraph.graph import StateGraph, START, END
from graph.nodes.post_review_node import PostReviewNode
from graph.nodes.bug_risk_review_node import BugRiskReviewNode
from graph.nodes.performance_review_node import PerformanceReviewNode
from graph.nodes.security_review_node import SecurityReviewNode
from graph.nodes.pr_review_node import PRReviewNode
from graph.nodes.final_review_node import FinalReviewNode
from graph.state import ReviewState
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
import dotenv
import os

dotenv.load_dotenv()
conn = sqlite3.connect(database= 'ai_code_review.db', check_same_thread=False)

builder = StateGraph(ReviewState)

# checkpointer
checkpointer = SqliteSaver(conn=conn)
os.environ['LANGCHAIN_TRACING_V2'] = 'true'

bug_risk_node= BugRiskReviewNode()
post_review_node = PostReviewNode()
performance_review_node = PerformanceReviewNode()
security_review_node = SecurityReviewNode()
pr_review_node = PRReviewNode()
final_review_node = FinalReviewNode()


builder.add_node("security_review", security_review_node.security_code_review_node)
builder.add_node("bug_risk_review", bug_risk_node.bug_risk_code_review_node)
builder.add_node("performance_review", performance_review_node.performance_code_review_node)
builder.add_node("pr_review", pr_review_node.pr_code_review_node)
builder.add_node("final_review", final_review_node.final_code_review_node)
builder.add_node("post_review", post_review_node.post_review)
builder.add_node("approve_review", post_review_node.approve_review)

builder.add_edge(START, "security_review")
builder.add_edge(START, "bug_risk_review")
builder.add_edge(START,  "performance_review")

builder.add_edge("security_review", "pr_review")
builder.add_edge("bug_risk_review", "pr_review")
builder.add_edge("performance_review", "pr_review")

builder.add_edge("pr_review", "final_review")

builder.add_edge("final_review", "approve_review")
builder.add_conditional_edges(
    "approve_review",
    post_review_node.approval_router
)
builder.add_edge("post_review", END)

graph = builder.compile(checkpointer=checkpointer)