
import json

from framework_core.ai_interface import AIEngine


class GenericErrorAgent:
    """
    AI Agent responsible for analyzing validation failures
    across the web application.
    """

    def __init__(self, config):
        self.engine = AIEngine(config)

    def analyze(self, context: dict) -> dict:
        prompt = self._build_prompt(context)
        return self.engine.generate(prompt)

    @staticmethod
    def _build_prompt(context: dict) -> str:
        return f"""
        You are an AI assistant specializing in test failure analysis.
        
        The automated test expected to find the following:
        
        Expected Text: {context['expected_text']}
        Expected Locator: {context['expected_locator']}
        
        The following error-like elements were found in the DOM:
        {json.dumps(context['error_candidates'], indent=2)}
        
        Here is a snapshot of the DOM:
        {context['dom'][:3000]}
        
        Please analyze why the expected text was not found.

        If you find an application error message, please include it in your response under the 'application_error_message' key.
        
        Please return ONLY a valid JSON object with the following structure:
        
        {
          "application_error_message": "<the exact UI error message if present, otherwise null>",
          "detected_error": "<a brief summary of the error>",
          "suggested_locator": "<an improved locator if applicable>",
          "reason": "<a clear explanation of what occurred>"
        }
        """
