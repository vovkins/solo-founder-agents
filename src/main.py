"""Main entry point for Solo Founder Agents."""

from config.settings import settings


def main():
    """Main function to run the application."""
    print("🚀 Solo Founder Agents")
    print(f"📦 Repository: {settings.github_repo}")
    print(f"🤖 Developer LLM: {settings.llm_developer}")
    print(f"👀 Reviewer LLM: {settings.llm_reviewer}")
    print("\nSystem initialized. Ready to process tasks.")


if __name__ == "__main__":
    main()
