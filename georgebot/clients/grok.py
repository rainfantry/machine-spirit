## ============================================================
## GROK.PY - xAI Grok brain
## ============================================================
## Uses xAI API. OpenAI-compatible syntax.
## ============================================================

import os
import sys
import json
import requests
from .base import BaseBrain


class GrokBrain(BaseBrain):
    """xAI Grok API client."""

    def __init__(self, api_key: str = None, model: str = "grok-4"):
        self.api_key = api_key or os.environ.get("GROK_API_KEY")
        self.model = model
        self.api_url = "https://api.x.ai/v1/chat/completions"

    @property
    def name(self) -> str:
        return f"grok:{self.model}"

    def chat(self, context: str, stream: bool = True) -> str:
        if not context or not self.api_key:
            return ""

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # Parse context into messages
        messages = self._parse_context(context)

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream
        }

        try:
            if stream:
                return self._stream_response(headers, payload)
            else:
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=60
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]

        except requests.HTTPError as e:
            print(f"[Grok HTTP error: {e}]")
            return ""
        except Exception as e:
            print(f"[Grok error: {e}]")
            return ""

    def _stream_response(self, headers, payload) -> str:
        response = requests.post(
            self.api_url,
            headers=headers,
            json=payload,
            stream=True,
            timeout=60
        )
        response.raise_for_status()

        full_response = ""
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        delta = chunk["choices"][0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            sys.stdout.write(content)
                            sys.stdout.flush()
                            full_response += content
                    except:
                        pass

        print()  # newline after stream
        return full_response

    def _parse_context(self, context: str) -> list:
        """Parse context string into messages list."""
        messages = []
        lines = context.strip().split('\n')

        current_role = None
        current_content = []

        for line in lines:
            if line.startswith("user:") or line.startswith("User:"):
                if current_role and current_content:
                    messages.append({
                        "role": current_role,
                        "content": "\n".join(current_content).strip()
                    })
                current_role = "user"
                current_content = [line.split(":", 1)[1].strip()]
            elif line.startswith("assistant:") or line.startswith("Assistant:"):
                if current_role and current_content:
                    messages.append({
                        "role": current_role,
                        "content": "\n".join(current_content).strip()
                    })
                current_role = "assistant"
                current_content = [line.split(":", 1)[1].strip()]
            else:
                # System prompt or continuation
                if current_role is None:
                    # First lines are system prompt
                    messages.append({"role": "system", "content": line})
                else:
                    current_content.append(line)

        # Don't forget last message
        if current_role and current_content:
            messages.append({
                "role": current_role,
                "content": "\n".join(current_content).strip()
            })

        # If no structured messages, treat whole thing as user message
        if not messages:
            messages = [{"role": "user", "content": context}]

        return messages

    def check(self) -> bool:
        if not self.api_key:
            return False
        try:
            response = requests.post(
                self.api_url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 5
                },
                timeout=10
            )
            return response.status_code == 200
        except:
            return False
