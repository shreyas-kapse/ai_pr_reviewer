from fastapi import FastAPI, Request
import traceback
from unidiff import PatchSet
import requests

from langchain_core.prompts import PromptTemplate
from services.llm_service import LLMService
from services.github_auth_service import GitHubAuthService
from graph.graph_builder import(graph)
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "server running"}


@app.post("/webhook/github")
async def github_webhook(request: Request):
    try:
        payload = await request.json()
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

        diff_text = response.text

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
        github_auth_service = GitHubAuthService()
        
        graph_response = graph.invoke({
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
        
def review_code(patch: str):

    prompt = PromptTemplate(template="""
    You are a senior software engineer reviewing a pull request.

    Review this git diff carefully.

    Focus on:
    - Bugs
    - Security issues
    - Performance problems
    - Code quality

    Keep feedback concise and actionable.

    Git Diff:
    {patch}
    """, input_variables=[patch])
    
    llm = LLMService.get_llm()

    response =llm.invoke(
        prompt.format(
        patch=patch
        )
    )
    print("\n response from LLM \n")
    print(response)
    return response.choices[0].message.content