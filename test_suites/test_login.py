
import allure


class TestInventory:

    @allure.id("Test_001")
    @allure.title("Test login with valid credentials")
    @allure.description("Verify whether user can login with valid credentials")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_valid_login(self, config, login):
        login.navigate()
        login.login(config.username, config.password)

    @allure.id("Test_002")
    @allure.title("Test Login with invalid credentials")
    @allure.description("Verify whether user can login with invalid credentials")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_valid_login_with_invalid_credentials(self, config, login):
        login.navigate()
        login.login(config.username, "secret_sauc")

    @allure.id("Test_003")
    @allure.title("Test inventory checkout without user information")
    @allure.description("Verify whether user can checkout without user information")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_checkout_without_user_information(self, config, login, inventory):
        login.navigate()
        login.login(config.username, config.password)
        inventory.checkout_complete(
            "Sauce Labs Backpack",
            "Vineeth",
            "Bandi",
            "75244"
        )
