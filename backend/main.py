from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import asyncio
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file before anything else
load_dotenv()

from jira_mcp_client import jira_mcp
from github_mcp_client import github_mcp
from planner_agent import planner_agent
from ticket_parser import ticket_parser
from pr_analyzer import pr_analyzer
from context_retriever import context_retriever
from semantic_search import semantic_search
from evidence_finder import evidence_finder
from test_generator import test_generator
from verdict_agent import verdict_agent
from dynamodb_client import dynamodb_client

app = FastAPI(title="Jira Ticket Evaluator API")

# Initialize DynamoDB Table on startup
dynamodb_client.create_table_if_not_exists()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js local server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EvaluationRequest(BaseModel):
    jira_id: str
    github_pr_url: str

@app.get("/")
def read_root():
    return {"status": "Backend is running"}

@app.post("/api/evaluate")
async def start_evaluation(request: EvaluationRequest):
    """
    Triggers the 10-stage evaluation pipeline.
    Stage 1 completes when this endpoint is hit.
    Stage 2: Fetch Jira Data
    Stage 4: Fetch GitHub Data
    """
    try:
        # Run Stage 2 and Stage 4 concurrently since they don't depend on each other
        jira_task = asyncio.create_task(jira_mcp.fetch_jira_ticket(request.jira_id))
        github_task = asyncio.create_task(github_mcp.fetch_github_pr(request.github_pr_url))
        
        jira_data, github_data = await asyncio.gather(jira_task, github_task)
        
        if not jira_data:
            raise HTTPException(status_code=404, detail=f"Could not fetch Jira Ticket {request.jira_id} via MCP")
            
        if not github_data:
            raise HTTPException(status_code=404, detail=f"Could not fetch GitHub PR {request.github_pr_url} via MCP")

        # Stage 2.5: Planner Agent - Decides the dynamic execution path
        plan = planner_agent.plan_execution(jira_data["raw_data"])
        execution_plan = plan.get("execution_plan", [])
        
        results_context: Dict[str, Any] = {}

        # Stage 3: Parse Jira Ticket with classification and search hints
        if "parse_ticket_requirements" in execution_plan:
            ticket_requirements = ticket_parser.parse_ticket_requirements(jira_data["raw_data"])
            results_context["requirements"] = ticket_requirements.get("requirements", [])
            results_context["ticket_type"] = ticket_requirements.get("ticket_type", plan.get("inferred_ticket_type"))

        # Stage 5: Analyze PR Structure (with requirements context)
        if "analyze_pr_structure" in execution_plan:
            req_statements = "\n".join([r['statement'] for r in results_context.get("requirements", [])])
            pr_structure = pr_analyzer.analyze_pr_structure(
                pr_metadata=github_data.get("pr_metadata", ""),
                pr_files=github_data.get("pr_files_diffs", ""),
                requirements_context=req_statements
            )
            results_context["pr_structure"] = pr_structure

        # Stage 5.5: Codebase Context Retriever - Fetch external file context
        external_context = []
        if "fetch_codebase_context" in execution_plan:
            # Extract owner/repo from URL
            pr_url = request.github_pr_url
            parts = pr_url.split("github.com/")[1].split("/")
            repo_full_name = f"{parts[0]}/{parts[1]}"
            
            external_context = await context_retriever.fetch_codebase_context(
                pr_diff=github_data.get("pr_files_diffs", ""),
                repo_full_name=repo_full_name
            )

        # Stage 6: Retrieve relevant Code Chunks (Semantic + Keyword search + External context)
        if "retrieve_relevant_code" in execution_plan:
            pr_files_dict = {"pr_changes.diff": github_data.get("pr_files_diffs", "")} 
            retrieved_chunks_map = semantic_search.process_pr_files_and_requirements(
                pr_files_dict=pr_files_dict, 
                requirements=results_context.get("requirements", []),
                external_context=external_context
            )
            results_context["retrieved_chunks"] = retrieved_chunks_map

        evidence_results = []
        test_results = []

        # Stage 7 & 8 Loop: Evidence Finder (with Validator) & Test Generator
        for req in results_context.get("requirements", []):
            # Stage 7: Evidence Finder + Validator (Retry Loop)
            if "find_requirement_evidence" in execution_plan:
                req_id_key = f"req_{req['id']}"
                relevant_chunks = results_context.get("retrieved_chunks", {}).get(req_id_key, [])
                
                evidence = evidence_finder.find_requirement_evidence(
                    requirement=req,
                    retrieved_code_chunks=relevant_chunks,
                    functional_map=results_context.get("pr_structure", {}),
                    pr_files_dict={"pr_changes.diff": github_data.get("pr_files_diffs", "")},
                    external_context=external_context
                )
                evidence_results.append(evidence)
            
            # Stage 8: Test Generator (Only if Planner approves)
            if "generate_and_run_tests" in execution_plan:
                # Passing the top retrieved chunk code snippet for test context
                code_context = relevant_chunks[0]["code"] if relevant_chunks else ""
                test_res = await test_generator.generate_and_run_tests(
                    requirement=req,
                    evidence=evidence if "find_requirement_evidence" in execution_plan else {},
                    code_snippet=code_context,
                    ticket_type=results_context.get("ticket_type", "feature")
                )
                test_results.append(test_res)

        # Stage 9: Final Verdict (with Planner decisions)
        if "generate_final_verdict" in execution_plan:
            final_verdict = verdict_agent.generate_final_verdict(
                requirements=results_context.get("requirements", []),
                evidence_results=evidence_results,
                test_results=test_results,
                planner_info=plan
            )
            # Add planner reasoning for display
            final_verdict["planner_decisions"] = plan.get("planner_reasoning", "")
            
            # Stage 10: Persist to DynamoDB 
            eval_id = dynamodb_client.save_evaluation(request.jira_id, request.github_pr_url, final_verdict)
            if eval_id:
                final_verdict["evaluation_id"] = eval_id
                
            return final_verdict
        
        return {"status": "success", "message": "Pipeline complete", "data": results_context}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
