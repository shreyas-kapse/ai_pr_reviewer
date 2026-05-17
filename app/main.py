from fastapi import FastAPI, HTTPException, Request
import traceback
from unidiff import PatchSet
import requests
import json
import os
from langchain_core.prompts import PromptTemplate
from services.llm_service import LLMService
from services.github_auth_service import GitHubAuthService
from graph.graph_builder import(build_graph)
from contextlib import asynccontextmanager


graph = None
saver_context = None

@asynccontextmanager
async def lifespan(app: FastAPI):

    global graph
    global saver_context

    graph, saver_context = (
        await build_graph()
    )
    yield
    if saver_context:

        await saver_context.__aexit__(
            None,
            None,
            None
        )

app = FastAPI(
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {"message": "server running"}


@app.post("/webhook/github")
async def github_webhook(request: Request):
    try:
        global graph

        github_auth_service = GitHubAuthService()
        
        raw_body = await request.body()
        
        # GITHUB SIGNATURE
        signature = request.headers.get(
            "X-Hub-Signature-256"
        )
        is_valid = (
            github_auth_service.verify_signature(
                payload_body=raw_body,
                signature_header=signature,
                secret=os.getenv(
                    "GITHUB_WEBHOOK_SECRET"
                )
            )
        )
        if not is_valid:
            raise HTTPException(
                status_code=401,
                detail="Invalid webhook signature"
            )
            
        payload = json.loads(raw_body)
        action = payload.get("action")
        
        # Only process PR opened/reopened/synchronize
        if action not in ["opened", "reopened", "synchronize"]:
            return {"message": "ignored event"}
        
        installation_id = payload["installation"]["id"]
        
        pull_request = payload["pull_request"]
        pr_number = pull_request["number"]
        repo_name = payload["repository"]["name"]
        owner = payload["repository"]["owner"]["login"]
        diff_url = pull_request["diff_url"]
        
        print("\n========== PR EVENT ==========")
        print("Action:", action)
        print("Repository:", repo_name)
        print("Owner:", owner)
        print("PR Number:", pr_number)
        print("Diff URL:", diff_url)
        
        print("\nFetching PR diff...")

        response = requests.get(diff_url)

        diff_text = response.text

        print("\n========== DIFF RESPONSE ==========")
        print("Status Code:", response.status_code)
        print("Headers:", response.headers)

        print("\n========== RAW DIFF ==========")
        print(diff_text[:1000])

        if not diff_text.strip():
            return {
                "error": "diff text is empty"
            }
        patch_set = PatchSet(diff_text)

        changed_files = []

        for patched_file in patch_set:

            file_data = {
                "file_name": patched_file.path,
                "added_lines": patched_file.added,
                "removed_lines": patched_file.removed,
                "patch": str(patched_file)
            }

            changed_files.append(file_data)

        print("\n========== CHANGED FILES ==========")

        for file in changed_files:
            print("\nFILE:", file["file_name"])
            print("Added:", file["added_lines"])
            print("Removed:", file["removed_lines"])

        print(changed_files)
        # review code
        # review_code(patch=patch_set)
        print("\n -----\n starting AI based code review")

        print("-----\n starting bug risk review")
        
        graph_response = await graph.ainvoke({
            "owner": owner,
            "repo": repo_name,
            "pr_number": pr_number,
            "installation_token": github_auth_service.get_installation_token(installation_id=installation_id),
            "changed_files": changed_files
        },
            config={
                "configurable": {
                    "thread_id": f"{repo_name}-{pr_number}"
                }
            })
        print(graph_response)
        return {
            "status": "success",
            "files_changed": len(changed_files)
        }

    except Exception as e:
        print("========== ERROR ==========")
        traceback.print_exc()

        return {
            "error": str(e)
        }