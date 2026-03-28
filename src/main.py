"""Main entry point for Solo Founder Agents."""

import sys

from config.settings import settings
from src.cli import cli
from src.pipeline import pipeline


def main():
    """Main function to run the application."""
    print("🚀 Solo Founder Agents")
    print(f"📦 Repository: {settings.github_repo}")
    print(f"🤖 Developer LLM: {settings.llm_developer}")
    print(f"👀 Reviewer LLM: {settings.llm_reviewer}")
    print("\nSystem initialized. Ready to process tasks.")


def run():
    """Run the CLI."""
    cli()


if __name__ == "__main__":
    run()
