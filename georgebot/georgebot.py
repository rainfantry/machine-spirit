#!/usr/bin/env python3
## ============================================================
## GEORGEBOT.PY - Multi-brain voice assistant
## ============================================================
## Swappable brains: ollama (local), grok (xAI), claude (anthropic)
## Voice: talkytalk (elevenlabs)
## ============================================================

import argparse
import sys
import os

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    get_brain, speak, SYSTEM_PROMPT,
    DEFAULT_BRAIN, DEFAULT_VOICE, RAG_DIR, MEMORY_DIR
)
from rag import RAGSearch
from session import Session
import re


def detect_and_store(text, rag):
    """
    Auto-detect patterns like 'my name is X' and store to RAG.
    Returns True if something was stored.
    """
    text_lower = text.lower()
    stored = []

    # Patterns to detect and extract
    patterns = [
        (r"my name is (\w+)", "name: {}"),
        (r"i am (\w+)", "identity: {}"),
        (r"call me (\w+)", "name: {}"),
        (r"i live in (.+?)(?:\.|$)", "location: {}"),
        (r"i work (?:at|for) (.+?)(?:\.|$)", "work: {}"),
        (r"i like (.+?)(?:\.|$)", "likes: {}"),
        (r"i hate (.+?)(?:\.|$)", "hates: {}"),
    ]

    for pattern, template in patterns:
        match = re.search(pattern, text_lower)
        if match:
            value = match.group(1).strip()
            note = template.format(value)
            rag.add_note(note)
            stored.append(note)

    return stored


def auto_search(text, rag):
    """
    Extract keywords from message, search RAG, return matches.
    """
    # Skip short messages
    if len(text) < 5:
        return ""

    # Common question words that suggest memory lookup
    memory_triggers = ["what", "who", "where", "my", "remember", "know"]

    text_lower = text.lower()
    should_search = any(trigger in text_lower for trigger in memory_triggers)

    if not should_search:
        return ""

    # Extract potential keywords (nouns, names)
    # Simple approach: words > 3 chars, not common words
    stopwords = {"what", "where", "when", "who", "how", "the", "is", "are", "was",
                 "were", "been", "being", "have", "has", "had", "does", "did",
                 "will", "would", "could", "should", "may", "might", "must",
                 "that", "this", "these", "those", "and", "but", "for", "with",
                 "about", "from", "into", "your", "you", "know", "tell", "remember"}

    words = re.findall(r'\b\w+\b', text_lower)
    keywords = [w for w in words if len(w) > 3 and w not in stopwords]

    if not keywords:
        return ""

    # Search for each keyword, collect results
    all_results = []
    seen = set()

    for keyword in keywords[:3]:  # Limit to 3 keywords
        results = rag.search(keyword)
        if results and results not in seen:
            seen.add(results)
            all_results.append(results)

    if all_results:
        return "\n".join(all_results)

    return ""


def print_banner(brain_name: str, rag_files: int = 0):
    print("""
 ╔═══════════════════════════════════════════════════════╗
 ║  GEORGEBOT v0.2                          George Wu    ║
 ║  Multi-brain Aussie Voice Agent                       ║
 ╠═══════════════════════════════════════════════════════╣
 ║  BRAINS (model <name>)                                ║
 ║  georgebot-chat   mistral 7b    fast banter           ║
 ║  georgebot-plan   deepseek 33b  slow architect        ║
 ║  georgebot-build  deepseek 6.7b fast coder            ║
 ╠═══════════════════════════════════════════════════════╣
 ║  COMMANDS                                             ║
 ║  exit       end session     brain <x>  switch api     ║
 ║  clear      wipe memory     model <x>  switch model   ║
 ║  models     list models     pull <x>   download       ║
 ║  files      knowledge       help       all commands   ║
 ╠═══════════════════════════════════════════════════════╣
 ║  MEMORY  "my name is X" auto-stores                   ║
 ║          "what is my name" auto-recalls               ║
 ╚═══════════════════════════════════════════════════════╝
""")
    print(f"  Brain: {brain_name}")
    print(f"  Knowledge files: {rag_files}")
    print("=" * 57)


def main():
    parser = argparse.ArgumentParser(description="Georgebot - Multi-brain assistant")
    parser.add_argument("--brain", "-b", default=DEFAULT_BRAIN,
                        choices=["ollama", "grok"],
                        help="Which brain to use")
    parser.add_argument("--no-voice", action="store_true",
                        help="Disable voice output")
    parser.add_argument("--list-brains", action="store_true",
                        help="List available brains")

    args = parser.parse_args()

    if args.list_brains:
        print("Available brains:")
        print("  ollama  - Local models (free, needs ollama installed)")
        print("  grok    - xAI Grok API (needs GROK_API_KEY)")
        return

    # Get brain
    try:
        brain = get_brain(args.brain)
    except Exception as e:
        print(f"Error loading brain: {e}")
        return

    # Check brain
    if not brain.check():
        print(f"[Warning: {brain.name} may not be available]")

    # Initialize RAG and Session
    rag = RAGSearch(str(RAG_DIR))
    rag_stats = rag.get_stats()

    print_banner(brain.name, rag_stats["file_count"])
    session = Session(memory_dir=str(MEMORY_DIR))

    # Startup voice
    if not args.no_voice:
        speak(f"georgebot online. using {args.brain}. whatcha need cunt.")

    # RAG context
    rag_context = ""

    # Main loop
    while True:
        try:
            user_input = input("\nYou> ").strip()

            if not user_input:
                continue

            # Commands
            if user_input.lower() in ("exit", "quit", "bye"):
                if not args.no_voice:
                    speak("later cunt.")
                print("Session ended.")
                break

            if user_input.lower() == "help":
                print("""
Commands:
  exit              - End session
  clear             - Clear conversation history
  brain <name>      - Switch brain (ollama, grok)
  load <topic>      - Load knowledge on topic
  remember <note>   - Save note to knowledge base
  files             - List knowledge files
  help              - Show this

Ollama Commands:
  models            - List installed models
  model <name>      - Switch ollama model
  pull <name>       - Download a model
  create            - Create custom georgebot model
""")
                continue

            if user_input.lower() == "models":
                from clients.ollama import OllamaBrain
                temp = OllamaBrain()
                print(temp.list_models())
                continue

            if user_input.lower().startswith("model "):
                new_model = user_input.split(maxsplit=1)[1].strip()
                if hasattr(brain, 'switch_model'):
                    brain.switch_model(new_model)
                else:
                    print("Only works with ollama brain")
                continue

            if user_input.lower().startswith("pull "):
                model_name = user_input.split(maxsplit=1)[1].strip()
                from clients.ollama import OllamaBrain
                temp = OllamaBrain()
                temp.pull_model(model_name)
                continue

            if user_input.lower() == "create":
                from clients.ollama import OllamaBrain, DEFAULT_SYSTEM_PROMPT
                print("Creating custom 'georgebot' model with default prompt...")
                print(f"System prompt:\n{DEFAULT_SYSTEM_PROMPT[:200]}...")
                temp = OllamaBrain()
                temp.create_model(
                    name="georgebot",
                    base_model="mistral:7b",
                    system_prompt=DEFAULT_SYSTEM_PROMPT
                )
                print("\nTo use: model georgebot")
                continue

            if user_input.lower() == "clear":
                session.clear()
                rag_context = ""
                print("Conversation and context cleared.")
                continue

            if user_input.lower().startswith("brain "):
                new_brain = user_input.split()[1]
                try:
                    brain = get_brain(new_brain)
                    print(f"Switched to {brain.name}")
                    if not args.no_voice:
                        speak(f"switched to {new_brain}")
                except Exception as e:
                    print(f"Error: {e}")
                continue

            if user_input.lower().startswith("load "):
                topic = user_input[5:].strip()
                if topic:
                    results = rag.search(topic)
                    if results:
                        rag_context = f"\n=== KNOWLEDGE: {topic} ===\n{results}\n=== END ===\n"
                        print(f"Loaded knowledge on: {topic}")
                        print(results[:500] + "..." if len(results) > 500 else results)
                        if not args.no_voice:
                            speak(f"loaded knowledge on {topic}")
                    else:
                        print(f"No knowledge found on: {topic}")
                        if not args.no_voice:
                            speak(f"nothing on {topic}")
                continue

            if user_input.lower().startswith("remember "):
                note = user_input[9:].strip()
                if note:
                    rag.add_note(note)
                    print(f"Saved: {note}")
                    if not args.no_voice:
                        speak("noted")
                continue

            if user_input.lower() == "files":
                files = rag.list_files()
                if files:
                    print("Knowledge files:")
                    for name, lines, size in files:
                        print(f"  {name} ({lines} lines, {size})")
                else:
                    print("No knowledge files yet. Use 'remember <note>' to create.")
                continue

            # === NATURAL LANGUAGE MEMORY ===
            # Auto-detect and store facts
            stored = detect_and_store(user_input, rag)
            if stored:
                print(f"[Remembered: {', '.join(stored)}]")

            # Auto-search for relevant knowledge
            auto_context = auto_search(user_input, rag)
            if auto_context:
                rag_context = f"\n=== MEMORY ===\n{auto_context}\n=== END ===\n"

            # Build context
            context = SYSTEM_PROMPT + "\n"
            if rag_context:
                context += rag_context + "\n"
            context += "\n"
            for role, content in session._messages:
                context += f"{role}: {content}\n"
            context += f"user: {user_input}\nassistant:"

            # Get response
            print("\nGeorgebot:")
            print("-" * 40)

            response = brain.chat(context)

            print("-" * 40)

            # Save to session
            session.add_message("user", user_input)
            session.add_message("assistant", response)

            # Voice
            if not args.no_voice and response:
                speak(response)

        except KeyboardInterrupt:
            print("\n[Interrupted]")
            continue

        except EOFError:
            break

    print("=" * 45)


if __name__ == "__main__":
    main()
