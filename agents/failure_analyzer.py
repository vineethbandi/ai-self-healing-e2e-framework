
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral"


class FailureAnalysisAgent:

    def __init__(self, config):
        self.config = config

    @staticmethod
    def classify_failure(locator, error_message):
        """
        Determines whether failure is likely due to locator mismatch.
        """

        # prompt = f"""
        # You are an automation debugging assistant.
        #
        # Locator used: {locator}
        # Error message: {error_message}
        #
        # Is this most likely:
        # 1. LOCATOR_MISMATCH
        # 2. PAGE_NOT_LOADED
        # 3. CREDENTIAL_ISSUE
        # 4. UNKNOWN
        #
        # Respond with only one option.
        # """
        #
        # response = requests.post(
        #     OLLAMA_URL,
        #     json={
        #         "model": MODEL,
        #         "prompt": prompt,
        #         "stream": False
        #     }
        # )
        #
        # result = response.choices[0].message.content.strip().upper()
        #
        # if "LOCATOR_MISMATCH" in result:
        #     return "LOCATOR_MISMATCH"
        # elif "TIMEOUT" in result:
        #     return "TIMEOUT"
        # elif "VISIBILITY" in result:
        #     return "VISIBILITY"
        # else:
        #     return "UNKNOWN"
        if "waiting for locator" in error_message.lower():
            return "LOCATOR_MISMATCH"

        if "timeout" in error_message.lower():
            return "TIMEOUT"

        if "not visible" in error_message.lower():
            return "VISIBILITY"

        return "UNKNOWN"

    def suggest_locator(self, old_locator, dom_buttons):
        prompt = f"""
        You are a Playwright expert with self-healing capabilities.

        The locator below has failed:
        {old_locator}

        Here are the available button elements:
        {dom_buttons}

        Please provide a valid CSS selector as a single line of text. Do not include any explanations or markdown formatting. For example: #login-button
        """

        response = requests.post(
            self.config.ollama_url,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False
            }
        )

        locator = response.json()["response"].strip()

        # Sanitize output
        locator = locator.replace("`", "").replace("```", "")
        locator = locator.split("\n")[0].strip()

        print("AI raw locator response:", locator)

        return locator

    @staticmethod
    def analyze_test_failure(error_message, url):
        """
        High-level test failure analysis.
        """

        prompt = f"""
        You are an expert automation debugging assistant.

        A test has failed with the following details:
        URL: {url}
        Error: {error_message}

        Please classify the failure from the following options:
        - LOCATOR_ISSUE
        - ASSERTION_FAILURE
        - BACKEND_ERROR
        - TEST_DATA_ISSUE
        - UNKNOWN

        Please also provide a brief explanation of the failure.
        """

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False
            }
        )

        return response.json()["response"].strip()
