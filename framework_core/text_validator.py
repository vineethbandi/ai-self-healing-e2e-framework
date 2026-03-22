
from agents.error_analyzer import GenericErrorAgent
from .dom_analyzer import DOMScanner

import allure


class IntelligentTextValidator:
    """
    Performs intelligent text validation on page elements. If the expected
    text is not found, this class collects contextual artifacts (scoped DOM,
    candidate error elements, screenshots), invokes an AI agent to analyze
    the failure, attaches relevant information to the test report, and raises
    a descriptive assertion to aid debugging.
    """

    def __init__(self, page, config):
        self.page = page
        self.config = config
        self.dom_scanner = DOMScanner(page)
        self.ai_agent = GenericErrorAgent(config)

    def validate_text(
            self,
            expected_locator: str,
            expected_text: str,
            parent_locator: str = None
        ):
        actual_text = None
        try:
            actual_text = self.page.locator(expected_locator).inner_text(timeout=5000)

            if expected_text in actual_text:
                print(f"Validation Passed: '{expected_text}' found")
                return True

        except Exception:
            pass

        # Validation failed: collect contextual artifacts and request AI analysis

        scoped_dom = self.dom_scanner.get_scoped_dom(parent_locator)
        error_candidates = self.dom_scanner.find_error_candidates(parent_locator)
        error_message = self._extract_error_message()

        context = {
            "expected_text": expected_text,
            "expected_locator": expected_locator,
            "error_candidates": error_candidates,
            "dom": scoped_dom,
            "application_error": error_message
        }

        print("\nAI test failure analysis starting...")

        ai_result = self.ai_agent.analyze(context)

        # Attach screenshot to Allure report for debugging
        screenshot_bytes = self.page.screenshot()
        allure.attach(
            screenshot_bytes,
            name="Text Validation Failure Screenshot",
            attachment_type=allure.attachment_type.PNG
        )

        # Attach expected vs. actual comparison
        allure.attach(
            f"Expected: {expected_text}\nActual: {actual_text}",
            name="Validation Details",
            attachment_type=allure.attachment_type.TEXT
        )

        # Raise an assertion with structured details returned from the AI analysis
        raise AssertionError(
            f"TEXT VALIDATION FAILED\n\n"
            f"Expected Text: '{expected_text}'\n"
            f"Expected Locator: '{expected_locator}'\n\n"
            f"Application Error Message: {ai_result.get('application_error_message')}\n\n"
            f"Detected Application Error: {ai_result.get('detected_error')}\n"
            f"Suggested Locator: {ai_result.get('suggested_locator')}\n"
            f"Reason: {ai_result.get('reason')}"
        )

    def _extract_error_message(self):
        possible_error_locators = [
            ".error-message-container h3",
            ".error-message-container",
            ".error",
            "[role='alert']",
            ".error-message"
        ]

        for locator in possible_error_locators:
            element = self.page.locator(locator)
            if element.count() > 0 and element.is_visible():
                return element.inner_text().strip()

        return None