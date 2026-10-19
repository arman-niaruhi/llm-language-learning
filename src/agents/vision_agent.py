"""Vision agent that turns an image into text context for the tutor agents."""

import base64
import os
from typing import Optional
from langchain_core.messages import HumanMessage
from src.agents.base_agent import BaseAgent
from src.schemas.messages import AgentType

DEFAULT_VISION_MODEL = "qwen3.5:4b"


class VisionAgent(BaseAgent):
    """Looks at an image and describes it so the other agents can work with it."""

    def __init__(self, model: Optional[str] = None):
        super().__init__(
            AgentType.VISION,
            model=model or os.getenv("VISION_MODEL", DEFAULT_VISION_MODEL),
            reasoning=False,
        )

    def describe(self, image: bytes, learning_language: str, question: str = "") -> str:
        """Return a plain-text description of the image for use as tutoring context."""
        prompt = (
            f"You are the vision component of a {learning_language} language-learning app. "
            "Another agent will use your answer to teach the learner, but it cannot see the image.\n"
            "Describe the image as plain text:\n"
            "1. Transcribe all visible text exactly as written, in its original language.\n"
            "2. List the main objects, people, actions and the setting.\n"
            "3. Mention anything useful for language learning (signs, labels, menus, grammar, items).\n"
            "Do not answer any question and do not add advice. Be factual and under 150 words."
        )
        if question:
            prompt += f"\nThe learner is asking: {question}\nFocus on details relevant to this."

        content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64.b64encode(image).decode()}"},
        ]
        return self.llm.invoke([HumanMessage(content=content)]).content.strip()
