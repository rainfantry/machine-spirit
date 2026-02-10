## ============================================================
## SESSION.PY - Session and memory management
## ============================================================
## Ported from Digger. Handles conversation history and persistence.
##
## What this does:
## 1. Creates a unique session ID (timestamp)
## 2. Tracks all messages (user + assistant)
## 3. Stores RAG context that was loaded
## 4. Saves everything to a file for persistence
## 5. Provides the full context to send to the model
## ============================================================

import os
from datetime import datetime
from pathlib import Path

try:
    from config import SYSTEM_PROMPT
except ImportError:
    SYSTEM_PROMPT = "You are a helpful assistant."


class Session:
    """
    Manages a single conversation session.

    Example:
        session = Session(memory_dir="./memory")
        session.add_context("TCP is a protocol...")
        session.add_message("user", "what is TCP")
        session.add_message("assistant", "TCP is...")

        context = session.get_context()  # Full context for model
    """

    def __init__(self, memory_dir="./memory"):
        """
        Initialize a new session.

        Args:
            memory_dir: Directory to store session files
        """
        ## Create unique session ID from timestamp
        self.id = datetime.now().strftime("%Y%m%d_%H%M%S")

        ## Setup paths
        self.memory_dir = Path(memory_dir)
        self.filepath = self.memory_dir / f"session_{self.id}.txt"

        ## Ensure memory directory exists
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        ## Initialize context storage
        self._rag_context = ""
        self._messages = []

        ## Create empty session file
        self._save()

    def add_context(self, content, topic=""):
        """
        Add RAG knowledge to the session context.

        This content will be included at the START of what the model sees.
        """
        if not content:
            return

        formatted = f"\n=== KNOWLEDGE ON '{topic}' ===\n{content}\n=== END KNOWLEDGE ===\n"

        self._rag_context += formatted
        self._save()

    def add_message(self, role, content):
        """
        Add a message to the conversation history.

        Args:
            role: Who said it ("user" or "assistant")
            content: What was said
        """
        if not content or not content.strip():
            return

        self._messages.append((role, content.strip()))
        self._save()

    def get_context(self):
        """
        Get the full context to send to the model.

        Returns:
            str: System prompt + RAG content + conversation history
        """
        context_parts = []

        ## System prompt FIRST
        context_parts.append(SYSTEM_PROMPT)

        ## RAG context
        if self._rag_context:
            context_parts.append(self._rag_context)

        ## Conversation history
        for role, content in self._messages:
            context_parts.append(f"{role}: {content}")

        return "\n".join(context_parts)

    def get_last_message(self, role=None):
        """
        Get the last message, optionally filtered by role.
        """
        for msg_role, content in reversed(self._messages):
            if role is None or msg_role == role:
                return content
        return ""

    def get_message_count(self):
        """
        Get the number of messages in the conversation.
        """
        return len(self._messages)

    def clear(self):
        """
        Clear everything - RAG context and conversation history.
        """
        self._rag_context = ""
        self._messages = []
        self._save()

    def clear_context(self):
        """
        Clear RAG context but keep conversation history.
        """
        self._rag_context = ""
        self._save()

    def _save(self):
        """
        Save the current session to disk.
        """
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                f.write(f"## Session: {self.id}\n")
                f.write(f"## Started: {datetime.now().isoformat()}\n")
                f.write("\n")

                if self._rag_context:
                    f.write("## === RAG CONTEXT ===\n")
                    f.write(self._rag_context)
                    f.write("\n")

                f.write("## === CONVERSATION ===\n")
                for role, content in self._messages:
                    f.write(f"{role}: {content}\n")

        except Exception as e:
            print(f"Warning: Could not save session: {e}")

    def get_summary(self):
        """
        Get a summary of the session for display.
        """
        return {
            "id": self.id,
            "filepath": str(self.filepath),
            "message_count": len(self._messages),
            "has_rag_context": bool(self._rag_context),
            "rag_context_length": len(self._rag_context),
        }


## ============================================================
## TEST
## ============================================================
if __name__ == "__main__":
    print("Testing session management...")
    print("=" * 50)

    session = Session(memory_dir="./memory")

    ## Add some RAG context
    session.add_context("TCP is a reliable transport protocol.", topic="TCP")

    ## Add conversation
    session.add_message("user", "what is TCP")
    session.add_message("assistant", "TCP guarantees delivery ya drongo.")
    session.add_message("user", "cheers dickhead")

    ## Get context
    print("\n--- Full Context ---")
    print(session.get_context())

    ## Show summary
    print("\n--- Summary ---")
    for key, value in session.get_summary().items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 50)
    print(f"Session saved to: {session.filepath}")
