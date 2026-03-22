
"""Pytest configuration for Playwright tests with Allure reporting and
AI-powered failure analysis.

This module defines fixtures used by tests (`page`, `config`, `login`,
`inventory`), ensures report directories exist, captures artifacts on
failure (screenshots, videos), and generates an Allure report at session
end. It also invokes an AI agent to analyze failed tests for debugging
assistance.
"""

import subprocess
import allure
import pytest
import shutil
import os

from playwright.sync_api import sync_playwright
from datetime import datetime

from agents.failure_analyzer import FailureAnalysisAgent
from configuration.config_reader import ConfigReader
from page_objects.login_page import LoginPage
from page_objects.inventory_page import Inventory

ALLURE_RESULTS_DIR = "allure-results"
ALLURE_REPORT_DIR = "allure-report"
ALLURE_HISTORY_DIR = os.path.join(ALLURE_REPORT_DIR, "history")


@pytest.fixture(scope="function")
def page(request):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context(record_video_dir='reports/videos/')
        page = context.new_page()
        yield page

        # Teardown: handle video saving and Allure attachment after test finishes
        video = page.video
        # Note: Playwright saves the video file when the browser context is closed
        context.close()  # context must be closed to flush recorded video

        if video:
            video_path = video.path()

            test_name = request.node.name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            new_name = f"{test_name}_{timestamp}.webm"
            new_path = os.path.join("reports/videos", new_name)

            os.rename(video_path, new_path)

            print(f"Video saved as: {new_path}")

            allure.attach.file(
                new_path,
                name="Execution Video",
                attachment_type=allure.attachment_type.WEBM
            )

        context.close()
        browser.close()

@pytest.fixture(scope="session")
def config():
    return ConfigReader()

@pytest.fixture
def login(page, config):
    return LoginPage(page, config)

@pytest.fixture
def inventory(page, config):
    return Inventory(page, config)

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page = item.funcargs.get("page", None)

        if page:
            error_message = str(report.longrepr)
            url = page.url

            # Capture a screenshot for debugging purposes
            page.screenshot(path="reports/screenshots/failure.png")

            # Perform AI-powered analysis of the failing test
            ai_result = FailureAnalysisAgent.analyze_test_failure(
                error_message,
                url
            )

            print("\nAI test failure analysis result:")
            print(ai_result)

def pytest_configure(config):
    # Ensure the test reporting directories exist before tests run
    os.makedirs("reports", exist_ok=True)
    os.makedirs("reports/screenshots", exist_ok=True)
    os.makedirs("reports/videos", exist_ok=True)

def pytest_sessionstart(session):
    """
    Copy previous Allure history before tests start.
    """
    if os.path.exists(ALLURE_HISTORY_DIR):
        history_dst = os.path.join(ALLURE_RESULTS_DIR, "history")

        if os.path.exists(history_dst):
            shutil.rmtree(history_dst)

        shutil.copytree(ALLURE_HISTORY_DIR, history_dst)
        print("Allure history copied successfully.")
    else:
        print("No previous Allure history found.")

def pytest_sessionfinish(session, exitstatus):
    """
    Generate Allure report automatically after tests finish.
    """
    print("\nGenerating Allure report...")

    subprocess.run(
        [
            "allure",
            "generate",
            ALLURE_RESULTS_DIR,
            "-o",
            ALLURE_REPORT_DIR,
            "--clean",
        ],
        check=False,
    )

    print("Allure report generated successfully.")
