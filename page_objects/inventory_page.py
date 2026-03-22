
import allure

from page_objects.base_page import BaseActions


class Inventory:
    """
    Page object encapsulating inventory and checkout flows used in tests.

    Provides high-level steps for adding items to cart and completing the
    checkout flow while delegating low-level interactions to `BaseActions`.
    """

    def __init__(self, page, config):
        self.page = page
        self.actions = BaseActions(page, config)

    @allure.step("Add inventory item and checkout: {inventory_name}")
    def add_inventory_and_checkout(self, inventory_name: str):
        """
        Selects an inventory item by visible name, adds it to the cart, and
        navigates to the checkout start.

        :param inventory_name: Exact product name as displayed on the page
        """
        # Click the 'Add to cart' button for the matching inventory item
        item = self.page.locator(".inventory_item", has_text=inventory_name)
        item.locator("button", has_text="Add to cart").click()

        # click on cart button
        self.actions.click("[data-test='shopping-cart-link']")

        # click on checkout
        self.actions.click("#checkout")

    @allure.step("Checkout: Your information: {first_name} {last_name} {zip_or_postal_code}")
    def checkout_your_information(self, first_name, last_name, zip_or_postal_code):
        """
        Fill in user information on the checkout form and continue to the
        overview step.

        :param first_name: First name
        :param last_name: Last name
        :param zip_or_postal_code: Zip/Postal code
        """
        self.actions.enter_text("#first-name", first_name)
        # Uncomment the following lines if last name and postal code fields
        # should be filled as part of the checkout flow.
        # self.actions.enter_text("#last-name", last_name)
        # self.actions.enter_text("#postal-code", zip_or_postal_code)
        self.actions.click("#continue")

        # Verify we've reached the overview page, scanning the `.error` scope
        # for application-level error messages if validation fails.
        self.actions.validate_text(
            expected_locator=".title",
            expected_text="Checkout: Overview",
            parent_locator=".error"
        )

    @allure.step("Checkout: Overview")
    def checkout_overview(self):
        """
        Complete the order from the overview step by clicking the final
        finish button and validating the completion message.
        """
        self.actions.click("#finish")

        self.actions.validate_text(
            expected_locator="[data-test='complete-header']",
            expected_text="Thank you for your order!"
        )

    @allure.step("Add inventory item and checkout complete: {inventory_name} {first_name} "
                 "{last_name} {zip_or_postal_code}")
    def checkout_complete(self, inventory_name, first_name, last_name, zip_or_postal_code):
        """
        Full scenario helper that performs the complete happy-path checkout
        flow using the other page methods.

        :param inventory_name: Inventory name
        :param first_name: First name
        :param last_name: Last name
        :param zip_or_postal_code: zip/postal code
        """
        self.add_inventory_and_checkout(inventory_name)
        self.checkout_your_information(first_name, last_name, zip_or_postal_code)
        self.checkout_overview()

        with allure.step('Order placed successfully.'):
            print('Order placed successfully.')
