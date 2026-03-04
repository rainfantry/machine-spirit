## ============================================================
## RAG.PY - Retrieval Augmented Generation search
## ============================================================
## Ported from Digger. Searches .md files for relevant content.
##
## BOUNDS LIMITS (prevent context overflow):
## - MAX_MATCHES_PER_FILE: Max matching sections per file
## - MAX_CONTEXT_LINES: Lines of context around each match
## - APPROX_CHAR_LIMIT: Total character limit (~2000 tokens)
## - MAX_FILES: Maximum number of files to include
## ============================================================

import os
import glob
import re
from pathlib import Path

## ============================================================
## BOUNDS LIMITS - Prevent context overflow
## ============================================================
MAX_MATCHES_PER_FILE = 3      ## Max matching sections per file
MAX_CONTEXT_LINES = 5         ## Lines before/after each match
APPROX_CHAR_LIMIT = 8000      ## ~2000 tokens max total
MAX_FILES = 5                 ## Max files to include in results


class RAGSearch:
    """
    Search engine for RAG knowledge base.

    Example:
        rag = RAGSearch("./RAG")
        results = rag.search("TCP")
        print(results)
    """

    def __init__(self, rag_dir="./RAG"):
        """
        Initialize RAG search.

        Args:
            rag_dir: Directory containing .md knowledge files
        """
        self.rag_dir = Path(rag_dir)
        self.rag_dir.mkdir(parents=True, exist_ok=True)

    def search(self, topic):
        """
        Search all .md files for a topic.

        Args:
            topic: Search term (case insensitive)

        Returns:
            str: Formatted results with source labels
        """
        if not topic or not topic.strip():
            return ""

        topic = topic.strip()
        results = []
        total_chars = 0
        files_included = 0

        ## Find all .md files
        md_files = sorted(glob.glob(str(self.rag_dir / "*.md")))

        if not md_files:
            return ""

        ## Search each file
        for filepath in md_files:
            if files_included >= MAX_FILES:
                break
            if total_chars >= APPROX_CHAR_LIMIT:
                break

            matches = self._search_file(filepath, topic)

            if matches:
                ## Check limit
                if total_chars + len(matches) > APPROX_CHAR_LIMIT:
                    remaining = APPROX_CHAR_LIMIT - total_chars
                    if remaining > 200:
                        matches = matches[:remaining] + "\n[...truncated...]"
                    else:
                        break

                filename = os.path.basename(filepath)
                formatted = f"[SOURCE: {filename}]\n{matches}"
                results.append(formatted)
                total_chars += len(formatted)
                files_included += 1

        return "\n\n".join(results)

    def _search_file(self, filepath, topic):
        """
        Search a single file for topic matches.
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Warning: Could not read {filepath}: {e}")
            return ""

        ## Find matching line numbers
        pattern = re.compile(re.escape(topic), re.IGNORECASE)
        match_indices = []

        for i, line in enumerate(lines):
            if pattern.search(line):
                match_indices.append(i)

        if not match_indices:
            return ""

        ## Limit matches per file
        match_indices = match_indices[:MAX_MATCHES_PER_FILE]

        ## Extract matches with context
        extracted = []
        seen_ranges = set()

        for idx in match_indices:
            start = max(0, idx - MAX_CONTEXT_LINES)
            end = min(len(lines), idx + MAX_CONTEXT_LINES + 1)

            section_lines = []
            for i in range(start, end):
                if i not in seen_ranges:
                    seen_ranges.add(i)
                    section_lines.append(lines[i].rstrip())

            if section_lines:
                extracted.append("\n".join(section_lines))

        return "\n--\n".join(extracted)

    def list_files(self):
        """
        List all knowledge base files.

        Returns:
            list: List of (filename, line_count, size_kb) tuples
        """
        files = []
        md_files = glob.glob(str(self.rag_dir / "*.md"))

        for filepath in sorted(md_files):
            try:
                filename = os.path.basename(filepath)
                line_count = sum(1 for _ in open(filepath, encoding="utf-8"))
                size_kb = os.path.getsize(filepath) / 1024
                files.append((filename, line_count, f"{size_kb:.1f}KB"))
            except Exception:
                pass

        return files

    def add_note(self, note, filename="notes.md"):
        """
        Add a note to the knowledge base.
        """
        from datetime import datetime

        filepath = self.rag_dir / filename

        with open(filepath, "a", encoding="utf-8") as f:
            f.write(f"\n## {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write(f"{note}\n")

    def get_stats(self):
        """
        Get stats about the knowledge base.
        """
        md_files = glob.glob(str(self.rag_dir / "*.md"))
        total_lines = 0
        total_size = 0

        for filepath in md_files:
            try:
                total_lines += sum(1 for _ in open(filepath, encoding="utf-8"))
                total_size += os.path.getsize(filepath)
            except Exception:
                pass

        return {
            "file_count": len(md_files),
            "total_lines": total_lines,
            "total_size_kb": f"{total_size / 1024:.1f}KB",
            "rag_dir": str(self.rag_dir),
        }


## ============================================================
## TEST
## ============================================================
if __name__ == "__main__":
    import sys

    print("Testing RAG search...")
    print("=" * 50)

    ## Use config to get rag_dir
    from config import load_config
    config = load_config()

    rag = RAGSearch(config["rag_dir"])

    ## Show stats
    print("\n--- Stats ---")
    stats = rag.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    ## List files
    print("\n--- Files ---")
    files = rag.list_files()
    if files:
        for filename, lines, size in files:
            print(f"  {filename} ({lines} lines, {size})")
    else:
        print("  (no files yet)")

    ## Test search if arg provided
    if len(sys.argv) > 1:
        topic = sys.argv[1]
        print(f"\n--- Search: '{topic}' ---")
        results = rag.search(topic)
        if results:
            print(results[:1000])
        else:
            print("No results.")

    print("\n" + "=" * 50)
