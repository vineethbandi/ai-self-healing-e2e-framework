
import allure

from page_objects.base_page import BaseActions


class LoginPage:
    """
    Page object for the application login flow.

    Provides navigation and login helpers that rely on `BaseActions` for
    resilient element interactions and validation.
    """

    def __init__(self, page, config):
        self.page = page
        self.config = config
        self.actions = BaseActions(page, config)

    def navigate(self):
        # Navigate to the application root and wait for DOM ready
        self.page.goto(self.config.base_url)
        self.page.wait_for_load_state("domcontentloaded")

    def login(self, username=None, password=None):
        username = username or self.config.username
        password = password or self.config.password

        # Fill credentials and submit login form
        # Note: locators should match the tested application's DOM
        self.actions.enter_text("#user-name", username)

        self.actions.enter_text("#password", password)

        self.actions.click("#login-button")

        # Validate a page element to ensure login succeeded; narrow the
        # scoped DOM search to `.login-box` to capture nearby application
        # error messages if validation fails.
        self.actions.validate_text(
            expected_locator=".app_logo",
            expected_text="Swag Labs",
            parent_locator=".login-box"
        )

        with allure.step('Login to saucedemo successfully.'):
            print('Login to saucedemo successfully.')
