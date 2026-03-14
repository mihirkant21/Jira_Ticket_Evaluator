import json
from bedrock_client import bedrock_client

# Stage 2.5 - Planner Agent (Claude Haiku 4.5)

class PlannerAgent:
    def __init__(self):
        self.system_prompt = """
        You are the Master Orchestrator (Planner Agent).
        You will receive the raw Jira ticket data. Your job is to deduce the ticket type and decide the execution plan.
        
        Available Pipeline Stages:
        1. parse_ticket_requirements
        2. fetch_github_pr
        3. analyze_pr_structure
        4. fetch_codebase_context  (New)
        5. retrieve_relevant_code
        6. find_requirement_evidence
        7. generate_and_run_tests  (Skip if ticket is a pure refactor)
        8. generate_final_verdict
        
        Instructions:
        1. Extract the implicit or explicit ticket type (feature / bug / refactor / infra).
        2. Output an ordered list of functions to execute.
        3. Explain WHY you are skipping any functions (like testing for a refactor).
        4. RETURN OUTPUT STRICTLY AS STRUCTURED VALID JSON.
        
        Expected output format:
        {
          "inferred_ticket_type": "refactor",
          "execution_plan": [
            "parse_ticket_requirements",
            "fetch_github_pr",
            "analyze_pr_structure",
            "fetch_codebase_context",
            "retrieve_relevant_code",
            "find_requirement_evidence",
            "generate_final_verdict"
          ],
          "skipped_stages": ["generate_and_run_tests"],
          "planner_reasoning": "This is a refactor ticket that shouldn't change outward behavior, thus skipping test generation."
        }
        """

    def plan_execution(self, jira_raw_data: str) -> dict:
        """
        Takes raw Jira data and uses Claude Haiku to map out the dynamic agentic plan (Stage 2.5).
        """
        prompt = f"{self.system_prompt}\n\nHere is the raw Jira Ticket data:\n{jira_raw_data}\n\nStrict JSON Output:"
        
        try:
            # We use Haiku 4.5 for fast dynamic planning
            response_text = bedrock_client.invoke_claude(
                prompt=prompt,
                model_id=bedrock_client.HAIKU_MODEL_ID,
                max_tokens=1000
            )
            
            if not response_text:
                return self._fallback_plan()
                
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
            
        except Exception as e:
            print(f"Error in Planner Agent: {e}")
            return self._fallback_plan()
            
    def _fallback_plan(self):
        return {
            "inferred_ticket_type": "feature",
            "execution_plan": [
                "parse_ticket_requirements", "fetch_github_pr", "analyze_pr_structure",
                "fetch_codebase_context", "retrieve_relevant_code", "find_requirement_evidence",
                "generate_and_run_tests", "generate_final_verdict"
            ],
            "skipped_stages": [],
            "planner_reasoning": "Fallback to full pipeline due to parsing error."
        }

planner_agent = PlannerAgent()
