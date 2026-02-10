## ============================================================
## OLLAMA.PY - Ollama model interaction
## ============================================================
## Ported from Digger. Talks to local LLM via subprocess.
##
## Subprocess is 2-3x faster than HTTP API.
## Direct pipe avoids serialization overhead.
## Streaming remains native-like.
##
## STDIN DEADLOCK FIX:
## process.stdin.write(context + "\n")
## process.stdin.flush()   # <-- Critical!
## process.stdin.close()   # <-- Critical!
## ============================================================

import subprocess
import sys
import re


class OllamaClient:
    """
    Client for interacting with Ollama models.

    Example:
        ollama = OllamaClient(model="mistral")
        response = ollama.chat("What is TCP?")
    """

    def __init__(self, model="mistral"):
        """
        Initialize Ollama client.

        Args:
            model: Ollama model name (e.g., "mistral", "llama3")
        """
        self.model = model

    def chat(self, context, stream=True):
        """
        Send context to model and get response.

        Args:
            context: Full context string (system prompt + RAG + conversation)
            stream: If True, print response as it arrives

        Returns:
            str: Complete response text
        """
        if not context or not context.strip():
            return ""

        try:
            ## Start ollama process
            ## bufsize=0 for unbuffered char-by-char streaming
            process = subprocess.Popen(
                ["ollama", "run", self.model],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False,  ## Binary mode for char-by-char
                bufsize=0    ## Unbuffered
            )

            ## CRITICAL: stdin flush fix for deadlock
            process.stdin.write((context + "\n").encode())
            process.stdin.flush()
            process.stdin.close()

            ## Collect response
            response = ""

            ## Stream output CHARACTER BY CHARACTER (typing effect)
            while True:
                char = process.stdout.read(1)
                if not char:
                    break
                decoded = char.decode('utf-8', errors='replace')
                response += decoded
                if stream:
                    sys.stdout.write(decoded)
                    sys.stdout.flush()

            process.wait()

            ## Check for errors
            stderr_output = process.stderr.read().decode('utf-8', errors='replace')
            if stderr_output:
                self._handle_stderr(stderr_output)

            return response.strip()

        except FileNotFoundError:
            print("[Error: Ollama not installed. Get it from https://ollama.ai]")
            return ""

        except Exception as e:
            print(f"[Ollama error: {e}]")
            return ""

    def _handle_stderr(self, stderr_output):
        """
        Handle stderr output from Ollama.
        Filters out spinner/progress ANSI codes.
        """
        ## Filter out ANSI escape sequences
        clean_stderr = re.sub(r'\x1b\[[0-9;?]*[a-zA-Z]', '', stderr_output)
        clean_stderr = re.sub(r'[⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏]', '', clean_stderr)
        clean_stderr = clean_stderr.strip()

        if not clean_stderr:
            return

        stderr_lower = clean_stderr.lower()

        if "model not found" in stderr_lower or "pull" in stderr_lower:
            print(f"\n[Error: Model '{self.model}' not found]")
            print(f"[Run: ollama pull {self.model}]")

        elif "connection refused" in stderr_lower:
            print("\n[Error: Ollama not running]")
            print("[Run: ollama serve]")

        elif clean_stderr:
            print(f"\n[Ollama stderr: {clean_stderr}]")

    def chat_no_stream(self, context):
        """
        Send context, return response without streaming.
        """
        return self.chat(context, stream=False)

    def check_model(self):
        """
        Check if the model is available.

        Returns:
            bool: True if model exists
        """
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return self.model in result.stdout

        except Exception:
            return False

    def list_models(self):
        """
        List available Ollama models.

        Returns:
            str: Output of 'ollama list'
        """
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout

        except FileNotFoundError:
            return "Error: Ollama not installed"

        except Exception as e:
            return f"Error: {e}"

    def create_model(self, modelfile_path, name=None):
        """
        Create a custom model from a Modelfile.

        Args:
            modelfile_path: Path to Modelfile
            name: Model name (default: self.model)

        Returns:
            bool: True if successful
        """
        name = name or self.model

        try:
            result = subprocess.run(
                ["ollama", "create", name, "-f", modelfile_path],
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                print(f"[Model '{name}' created]")
                return True
            else:
                print(f"[Error creating model: {result.stderr}]")
                return False

        except Exception as e:
            print(f"[Error: {e}]")
            return False

    def pull_model(self):
        """
        Pull/download the model.

        Returns:
            bool: True if successful
        """
        try:
            print(f"[Pulling model '{self.model}'...]")

            process = subprocess.Popen(
                ["ollama", "pull", self.model],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            for line in process.stdout:
                print(line, end="", flush=True)

            process.wait()
            return process.returncode == 0

        except Exception as e:
            print(f"[Error: {e}]")
            return False

    def switch_model(self, new_model):
        """
        Switch to a different model.

        Args:
            new_model: New model name

        Returns:
            bool: True if model exists
        """
        old_model = self.model
        self.model = new_model

        if self.check_model():
            print(f"[Switched: {old_model} -> {new_model}]")
            return True
        else:
            print(f"[Model '{new_model}' not found. Staying on {old_model}]")
            self.model = old_model
            return False


## ============================================================
## TEST
## ============================================================
if __name__ == "__main__":
    print("Testing Ollama client...")
    print("=" * 50)

    model = sys.argv[1] if len(sys.argv) > 1 else "mistral"
    ollama = OllamaClient(model=model)

    ## List models
    print("\n--- Available Models ---")
    print(ollama.list_models())

    ## Check if model exists
    print(f"\n--- Checking model '{model}' ---")
    if ollama.check_model():
        print(f"Model '{model}' is available")

        ## Test chat
        print("\n--- Test Chat ---")
        print("Sending: 'Say hello in 5 words or less'")
        print("-" * 30)

        response = ollama.chat("Say hello in 5 words or less")

        print("-" * 30)
        print(f"\nResponse length: {len(response)} chars")
    else:
        print(f"Model '{model}' not found!")
        print(f"Run: ollama pull {model}")

    print("=" * 50)
