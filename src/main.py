"""Console application for language learning with multi-agent system."""

from dotenv import load_dotenv
from src.agents.coordinator_agent import CoordinatorAgent
from src.agents.vocabulary_agent import VocabularyAgent
from src.agents.grammar_agent import GrammarAgent
from src.agents.conversation_agent import ConversationAgent
from src.schemas.messages import AgentState


class LanguageLearningConsole:
    """Interactive console for language learning."""

    def __init__(self):
        load_dotenv()

        # Initialize agents
        self.coordinator = CoordinatorAgent()
        self.vocabulary_agent = VocabularyAgent()
        self.grammar_agent = GrammarAgent()
        self.conversation_agent = ConversationAgent()

        # Register agents with coordinator
        self.coordinator.register_agent(self.vocabulary_agent)
        self.coordinator.register_agent(self.grammar_agent)
        self.coordinator.register_agent(self.conversation_agent)

        self.learning_language = "English"
        self.difficulty_level = "beginner"

    def process_input(self, user_input: str) -> str:
        """Process user input through the coordinator."""
        state = AgentState(
            user_input=user_input,
            learning_language=self.learning_language,
            difficulty_level=self.difficulty_level
        )

        result = self.coordinator.graph.invoke(state)
        if not result.get("response"):
            return "No response generated"
        return f"[{result['current_agent'].upper()}]\n{result['response']}"

    def show_menu(self) -> None:
        """Display main menu."""
        print("\n" + "="*60)
        print("🎓 LANGUAGE LEARNING SYSTEM - Multi-Agent Coordinator")
        print("="*60)
        print(f"Learning Language: {self.learning_language}")
        print(f"Difficulty Level: {self.difficulty_level}")
        print("-"*60)
        print("Commands:")
        print("  /lang <language>     - Change learning language")
        print("  /level <difficulty>  - Change difficulty (beginner/intermediate/advanced)")
        print("  /menu                - Show this menu")
        print("  /quit                - Exit")
        print("  Or enter your question/request")
        print("="*60)

    def parse_command(self, user_input: str) -> bool:
        """Parse and execute commands. Returns True if input is a command."""
        if user_input.startswith("/"):
            parts = user_input.split(maxsplit=1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""

            if command == "/lang":
                if args:
                    self.learning_language = args
                    print(f"✓ Changed language to: {self.learning_language}")
                else:
                    print("Please specify a language (e.g., /lang Spanish)")
                return True

            elif command == "/level":
                if args in ["beginner", "intermediate", "advanced"]:
                    self.difficulty_level = args
                    print(f"✓ Changed difficulty to: {self.difficulty_level}")
                else:
                    print("Invalid level. Use: beginner, intermediate, or advanced")
                return True

            elif command == "/menu":
                self.show_menu()
                return True

            elif command == "/quit":
                print("\nGoodbye! Keep learning! 👋")
                return False

        return True

    def run(self) -> None:
        """Run the interactive console."""
        # Check if Ollama is running
        try:
            import requests
            requests.get("http://localhost:11434", timeout=2)
        except Exception:
            print("\n⚠️  Warning: Ollama does not appear to be running.")
            print("Start Ollama with: ollama serve")
            print(f"Make sure to pull a model first: ollama pull {self.coordinator.model}\n")

        self.show_menu()

        while True:
            try:
                user_input = input("\n📝 You: ").strip()

                if not user_input:
                    continue

                # Check for commands
                if user_input.startswith("/"):
                    if not self.parse_command(user_input):
                        break
                    continue

                # Process with agents
                print("\n🤖 Processing with agent system...")
                response = self.process_input(user_input)
                print(f"\n🎯 Response:\n{response}")

            except KeyboardInterrupt:
                print("\n\nInterrupted. Type /quit to exit or continue...")
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                print("Make sure Ollama is running: ollama serve")


def main():
    """Main entry point."""
    LanguageLearningConsole().run()


if __name__ == "__main__":
    main()
