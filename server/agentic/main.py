# --- OpenAI-based version ---
from __future__ import annotations

import os
import json
import subprocess
import tempfile
from typing import Any, Dict, List

from dotenv import load_dotenv
from fastapi import HTTPException  # only if you use it elsewhere
from pydantic import BaseModel

# LangChain (OpenAI)
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

load_dotenv()


# ──────────────────────────────────────────────────────────────────────────────
# Static code checks (unchanged)
# ──────────────────────────────────────────────────────────────────────────────
class CodeChecker:
    """Run Pylint on an in-memory Python string."""
    @staticmethod
    def check_code_with_pylint(code_string: str) -> str:
        if not code_string.strip():
            return "Error: Empty code string provided. Pylint cannot check empty code."

        tmp = None
        try:
            with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
                f.write(code_string)
                tmp = f.name

            result = subprocess.run(
                ["pylint", tmp],
                capture_output=True,
                text=True,
                timeout=20,
            )
            return result.stdout.strip()
        except FileNotFoundError:
            return "Error: 'pylint' not found. Is it installed and on PATH?"
        except (subprocess.TimeoutExpired, OSError) as e:
            return f"An error occurred while running Pylint: {e}"
        finally:
            if tmp and os.path.exists(tmp):
                try:
                    os.unlink(tmp)
                except OSError:
                    pass


# ──────────────────────────────────────────────────────────────────────────────
# OpenAI Agent (LangChain)
# ──────────────────────────────────────────────────────────────────────────────
class Assistant_agent:
    """
    AI Code Review Tutor (OpenAI + LangChain).
    Returns a single JSON object as a string (schema enforced via prompt).
    """

    MAIN_PROMPT = """You are an AI Code Review Tutor. Your purpose is to provide structured, educational feedback on code quality and design patterns.

You MUST return a single valid JSON object and nothing else. No prose outside JSON.

Schema:
{
  "answer": "Short, encouraging summary of the main area for improvement (max 2 sentences).",
  "hints": [
    "Conceptual/strategic suggestion (e.g., 'Review the State pattern...').",
    "Hint referencing a style/naming/structure issue (can leverage Pylint).",
    "Final brief guidance."
  ]
}
"""

    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.4):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("Missing OPENAI_API_KEY in environment (.env).")

        self.model_name = model_name
        self.temperature = temperature
        self.conversation_history: List[AIMessage | HumanMessage] = []

        # Base LLM (general replies)
        self.llm = ChatOpenAI(
            api_key=self.openai_api_key,
            model=self.model_name,
            temperature=self.temperature,
        )

        # JSON-enforcing LLM (for review outputs)
        self.json_llm = ChatOpenAI(
            api_key=self.openai_api_key,
            model=self.model_name,
            temperature=self.temperature,
            # Ask OpenAI to return a JSON object (supported by newer models)
            model_kwargs={"response_format": {"type": "json_object"}},
        )

    def run(self, problem: str, pylint_report: str, reference_solution: str, user_code: str) -> str:
        """
        Analyze code and return a JSON string. If the model returns non-JSON,
        we attempt to coerce/validate.
        """
        user_payload = f"""
**Context Variables for Analysis:**
- problem: {problem}
- code clean score (pylint): {pylint_report}
- reference_solution: {reference_solution}
- user_code: {user_code}

**Output Requirements**
- Return ONLY a single JSON object, no markdown.
- Be more theoretical when giving hints (explain the technique).
- Point to specific code areas that each hint applies to.
- Include: "score" (0..100) assessing the code quality.

Strict JSON schema:
{{
  "answer": "...",
  "hints": [
    "concept/design pattern guidance",
    "naming/structure/pylint-aligned hint",
    "pythonic/maintainability hint"
  ],
  "score": 0
}}
""".strip()

        messages = [
            SystemMessage(content=self.MAIN_PROMPT),
            *self.conversation_history,
            HumanMessage(content=user_payload),
        ]

        # Use JSON-enforcing LLM
        resp = self.json_llm.invoke(messages)

        # Keep history
        self.conversation_history.append(HumanMessage(content=user_payload))
        self.conversation_history.append(AIMessage(content=resp.content))

        # Best-effort JSON validation
        content = resp.content.strip()
        try:
            _ = json.loads(content)  # validate JSON
            return content
        except json.JSONDecodeError:
            # Fallback: wrap into a JSON object
            return json.dumps({
                "answer": "The assistant produced a non-JSON reply; here is a safe wrapper.",
                "hints": [content[:300]],
                "score": 0
            })

    def invoke_llm_for_chat(self, data: Dict) -> Dict[str, Any]:
        prompt = f"""You are an expert programming mentor on clean code & design patterns.

Provided: {data}

Instructions:
- Give practical, concise advice.
- Use examples when helpful.
- Ask clarifying questions if needed.
- Prefer actionable steps over theory.
"""
        resp = self.llm.invoke(prompt)
        return {"message": resp.content}

    # Conversation utils
    def clear_history(self) -> None:
        self.conversation_history = []

    def get_history(self) -> List[AIMessage | HumanMessage]:
        return self.conversation_history

    def get_history_summary(self) -> str:
        out = []
        for i, msg in enumerate(self.conversation_history, 1):
            role = "User" if isinstance(msg, HumanMessage) else "AI"
            out.append(f"[{i}] {role}: {msg.content[:100]}...")
        return "\n".join(out)


# --- Example usage ---
if __name__ == "__main__":
    problem = "Adapt a Fahrenheit-only sensor to a Celsius interface."
    user_code = """
class FahrenheitSensor:
    def read_f(self) -> float:
        return 77.0

class CelsiusReader:
    def read_c(self) -> float: ...

class FahrenheitToCelsiusAdapter(CelsiusReader):
    def __init__(self, sensor: FahrenheitSensor):
        self.sensor = sensor
    def read_c(self) -> float:
        f = self.sensor.read_f()
        return (f - 32) * 5.0/9.0

def main():
    sensor = FahrenheitSensor()
    adapter = FahrenheitToCelsiusAdapter(sensor)
    print(adapter.read_c())
"""
    correct_code = user_code

    try:
        pylint_result = CodeChecker.check_code_with_pylint(user_code)
    except Exception as e:
        pylint_result = f"Pylint check failed: {e}"

    agent = Assistant_agent()
    result_json = agent.run(problem, pylint_result, correct_code, user_code)
    print(result_json)
