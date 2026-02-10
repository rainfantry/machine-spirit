## ============================================================
## OLLAMA.PY - Local Ollama brain
## ============================================================
## Free. Local. No API cost. Needs ollama installed.
## ============================================================

import subprocess
import sys
import re
import os
from .base import BaseBrain


def find_ollama() -> str:
    """Find ollama executable - check PATH then known locations."""
    # Check if in PATH
    try:
        result = subprocess.run(
            ["where", "ollama"] if sys.platform == "win32" else ["which", "ollama"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return "ollama"  # Found in PATH
    except:
        pass

    # Windows known locations
    if sys.platform == "win32":
        locations = [
            os.path.expanduser("~\\AppData\\Local\\Programs\\Ollama\\ollama.exe"),
            "C:\\Program Files\\Ollama\\ollama.exe",
            "C:\\Program Files (x86)\\Ollama\\ollama.exe",
        ]
        for loc in locations:
            if os.path.exists(loc):
                return loc

    return "ollama"  # Fallback to hoping it's in PATH


OLLAMA_PATH = find_ollama()


class OllamaBrain(BaseBrain):
    """Local Ollama model client."""

    def __init__(self, model: str = "mistral"):
        self.model = model
        self.ollama = OLLAMA_PATH

    @property
    def name(self) -> str:
        return f"ollama:{self.model}"

    def chat(self, context: str, stream: bool = True) -> str:
        if not context or not context.strip():
            return ""

        try:
            process = subprocess.Popen(
                [self.ollama, "run", self.model],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False,
                bufsize=0
            )

            process.stdin.write((context + "\n").encode())
            process.stdin.flush()
            process.stdin.close()

            response = ""
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
            return response.strip()

        except FileNotFoundError:
            print("[Error: Ollama not installed]")
            return ""
        except Exception as e:
            print(f"[Ollama error: {e}]")
            return ""

    def check(self) -> bool:
        try:
            result = subprocess.run(
                [OLLAMA_PATH, "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return self.model in result.stdout
        except:
            return False

    def list_models(self) -> str:
        try:
            result = subprocess.run(
                [OLLAMA_PATH, "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout
        except:
            return "Error: Ollama not available"

    def create_model(self, name: str, base_model: str, system_prompt: str,
                     temperature: float = 0.7, num_ctx: int = 4096) -> bool:
        """
        Create a custom model with system prompt.

        Args:
            name: New model name
            base_model: Base model (e.g., 'mistral:7b')
            system_prompt: System prompt to bake in
            temperature: Creativity (0.0-1.0)
            num_ctx: Context window size

        Returns:
            bool: True if successful
        """
        import tempfile
        import os

        # Create Modelfile content
        modelfile_content = f'''FROM {base_model}

SYSTEM "{system_prompt}"

PARAMETER temperature {temperature}
PARAMETER num_ctx {num_ctx}
'''

        # Write to temp file
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.Modelfile',
                                              delete=False) as f:
                f.write(modelfile_content)
                modelfile_path = f.name

            # Create the model
            print(f"[Creating model '{name}' from {base_model}...]")
            result = subprocess.run(
                [OLLAMA_PATH, "create", name, "-f", modelfile_path],
                capture_output=True,
                text=True,
                timeout=120
            )

            # Cleanup temp file
            os.unlink(modelfile_path)

            if result.returncode == 0:
                print(f"[Model '{name}' created successfully]")
                return True
            else:
                print(f"[Error: {result.stderr}]")
                return False

        except Exception as e:
            print(f"[Error creating model: {e}]")
            return False

    def create_from_file(self, modelfile_path: str, name: str = None) -> bool:
        """
        Create model from existing Modelfile.

        Args:
            modelfile_path: Path to Modelfile
            name: Model name (default: self.model)

        Returns:
            bool: True if successful
        """
        name = name or self.model

        try:
            print(f"[Creating model '{name}' from {modelfile_path}...]")
            result = subprocess.run(
                [OLLAMA_PATH, "create", name, "-f", modelfile_path],
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                print(f"[Model '{name}' created]")
                return True
            else:
                print(f"[Error: {result.stderr}]")
                return False

        except Exception as e:
            print(f"[Error: {e}]")
            return False

    def pull_model(self, model: str = None) -> bool:
        """
        Pull/download a model.

        Args:
            model: Model name (default: self.model)

        Returns:
            bool: True if successful
        """
        model = model or self.model

        try:
            print(f"[Pulling model '{model}'...]")

            process = subprocess.Popen(
                [OLLAMA_PATH, "pull", model],
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

    def switch_model(self, new_model: str) -> bool:
        """
        Switch to a different model.

        Args:
            new_model: New model name

        Returns:
            bool: True if model exists
        """
        old_model = self.model
        self.model = new_model

        if self.check():
            print(f"[Switched: {old_model} -> {new_model}]")
            return True
        else:
            print(f"[Model '{new_model}' not found]")
            self.model = old_model
            return False


# Default system prompt for georgebot
DEFAULT_SYSTEM_PROMPT = """You are Georgebot, George Wu's Australian assistant.
Swear naturally - fuck, shit, cunt, dickhead, drongo.
Answer questions directly first, then roast if appropriate.
Never be fake polite. Never say 'certainly' or 'I'd be happy to'.
Use aussie slang - mate, ay, nah, yeah, cos, gonna.
Keep it real. Keep it short. One response only."""
