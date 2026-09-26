import json
from typing import Any, Dict, List
import aisuite as ai
from pydantic import BaseModel, Field

# ==========================================
# 1. Native Tool Definitions
# ==========================================

def read_mail(mail_id: str) -> Dict[str, Any]:
    return {
        "status": "success",
        "result": f"Content of email '{mail_id}': 'Please review the Q3 budget report.'"
    }

def write_reply(mail_id: str, body: str) -> Dict[str, Any]:
    return {
        "status": "success",
        "result": f"Sent reply to email '{mail_id}' with message: '{body}'"
    }

def search_mail(query: str) -> Dict[str, Any]:
    return {
        "status": "success",
        "result": [f"mail_101 (Subject: Urgent - {query})", f"mail_102 (Subject: Re: {query})"]
    }

def move_mail(mail_id: str, folder: str) -> Dict[str, Any]:
    return {
        "status": "success",
        "result": f"Moved email '{mail_id}' to folder '{folder}'."
    }

def delete_mail(mail_id: str) -> Dict[str, Any]:
    return {
        "status": "success",
        "result": f"Deleted email '{mail_id}'."
    }

# Mapping string names to native functions
TOOL_REGISTRY = {
    "read_mail": read_mail,
    "write_reply": write_reply,
    "search_mail": search_mail,
    "move_mail": move_mail,
    "delete_mail": delete_mail
}

# ==========================================
# 2. Pydantic Models for JSON Plan Validation
# ==========================================

class PlanStep(BaseModel):
    step_id: int = Field(description="Sequential step number starting from 1")
    action: str = Field(description="Exact tool name to call")
    parameters: Dict[str, Any] = Field(description="Arguments required for the tool")

class ExecutionPlan(BaseModel):
    task: str = Field(description="Overview of the prompt objective")
    plan: List[PlanStep] = Field(description="List of execution steps in order")

# ==========================================
# 3. AISuite Email Agent
# ==========================================

SYSTEM_PROMPT = """
You are an Email Automation Agent.
Your job is to parse user requests and convert them into a structured JSON plan using the available tools.

Available Tools:
- search_mail(query: str)
- read_mail(mail_id: str)
- write_reply(mail_id: str, body: str)
- move_mail(mail_id: str, folder: str)
- delete_mail(mail_id: str)

Rules:
1. Always respond ONLY with a valid JSON object matching this schema:
{
  "task": "description",
  "plan": [
    {
      "step_id": 1,
      "action": "tool_name",
      "parameters": {"param_name": "value"}
    }
  ]
}
2. Ensure step order is strictly logical.
3. Use placeholder IDs like 'mail_101' when referencing emails from prior search steps.
"""

class AISuiteEmailAgent:
    def __init__(self, model_provider: str = "openai:gpt-4o"):
        # Initialize AISuite Client
        self.client = ai.Client()
        self.model_provider = model_provider

    def create_json_plan(self, user_prompt: str) -> ExecutionPlan:
        """Uses AISuite to query the LLM and return a validated JSON execution plan."""
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Create an execution plan for: {user_prompt}"}
        ]

        # Call the model via AISuite interface
        response = self.client.chat.completions.create(
            model=self.model_provider,
            messages=messages,
            temperature=0.1,
            response_format={"type": "json_object"}
        )

        raw_json = response.choices[0].message.content
        # Validate JSON output with Pydantic
        return ExecutionPlan.model_validate_json(raw_json)

    def execute_plan(self, plan: ExecutionPlan) -> List[Dict[str, Any]]:
        """Parses the generated plan and executes registered Python tool functions."""
        execution_logs = []
        print(f"\n--- Executing Plan for Task: '{plan.task}' ---")

        for step in plan.plan:
            action = step.action
            params = step.parameters

            if action not in TOOL_REGISTRY:
                err_msg = f"Tool '{action}' not found in registry."
                print(f"[Error] {err_msg}")
                execution_logs.append({"step_id": step.step_id, "status": "failed", "error": err_msg})
                continue

            print(f"[Step {step.step_id}] Executing `{action}` with params: {params}")
            
            # Execute local Python function
            tool_fn = TOOL_REGISTRY[action]
            output = tool_fn(**params)

            execution_logs.append({
                "step_id": step.step_id,
                "action": action,
                "output": output
            })
            print(f" -> Output: {output['result']}\n")

        return execution_logs

    def run(self, user_prompt: str):
        print(f"User Request: \"{user_prompt}\"")

        # Step 1: Generate plan using AISuite
        plan = self.create_json_plan(user_prompt)
        print("\n--- Generated JSON Plan ---")
        print(json.dumps(plan.model_dump(), indent=2))

        # Step 2: Execute the plan sequentially
        results = self.execute_plan(plan)
        return results

# ==========================================
# 4. Usage Example
# ==========================================

if __name__ == "__main__":
    # You can swap 'openai:gpt-4o' with 'anthropic:claude-3-5-sonnet' or 'groq:llama-3.3-70b'
    #also you can use 'openai:gpt-4o-mini' for a smaller model variant.
    agent = AISuiteEmailAgent(model_provider="openai:gpt-4o")

    prompt = (
        "Search for emails regarding 'budget', read email mail_101, "
        "reply with 'Approved', and move mail_101 to 'Archive'."
    )

    agent.run(prompt)