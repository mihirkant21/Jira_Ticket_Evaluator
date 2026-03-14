import json
from bedrock_client import bedrock_client

# Stage 3 - Ticket Parser Agent (Claude Haiku 4.5)

class TicketParser:
    def __init__(self):
        self.system_prompt = """
        You are an expert Agile Business Analyst.
        Your job is to read a raw Jira ticket JSON and extract every individual requirement as a clean, atomic, testable statement.
        
        Instructions:
        1. Break vague descriptions into specific, testable requirements.
        2. Number each requirement clearly.
        3. Identify the ticket type (feature / bug / refactor).
        4. Classify each requirement into a type:
           - behavioral: system logic/behavior
           - security: data protection, Auth, encryption
           - UI: visual elements, components
           - performance: caching, optimization
           - refactor: structural changes
        5. For each requirement, provide 2-3 'search_hints' (keywords or patterns) that would help find relevant code.
        6. RETURN OUTPUT STRICTLY AS STRUCTURED VALID JSON. Do not include markdown formatting or explanations outside the JSON.
        
        Expected output format:
        {
          "ticket_type": "feature",
          "requirements": [
            { 
              "id": 1, 
              "statement": "Reset email must be sent to user",
              "classification": "behavioral",
              "search_hints": ["email", "smtp", "send_mail"]
            }
          ]
        }
        """

    def parse_ticket_requirements(self, jira_raw_data: str) -> dict:
        """
        Takes raw Jira data and uses Claude Haiku to extract atomic requirements (Stage 3).
        """
        prompt = f"{self.system_prompt}\n\nHere is the raw Jira Ticket data:\n{jira_raw_data}\n\nStrict JSON Output:"
        
        try:
            # We use Haiku 4.5 for fast, cheap abstraction of the ticket structure
            response_text = bedrock_client.invoke_claude(
                prompt=prompt,
                model_id=bedrock_client.HAIKU_MODEL_ID,
                max_tokens=1500
            )
            
            if not response_text:
                return {"ticket_type": "unknown", "requirements": []}
                
            # Claude sometimes pads output with backticks, clean it
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            
            return json.loads(clean_text)
            
        except json.JSONDecodeError:
            print("Failed to parse Claude Ticket Output as JSON")
            return {"ticket_type": "unknown", "requirements": []}
        except Exception as e:
            print(f"Error in Ticket Parser: {e}")
            return {"ticket_type": "unknown", "requirements": []}

ticket_parser = TicketParser()
