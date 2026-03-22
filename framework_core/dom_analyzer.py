

class DOMScanner:
    """
    Utility for extracting DOM snippets from a Playwright `page` and
    for discovering elements that commonly represent error messages or
    alerts. Methods return simple, safe defaults on failure so callers
    can continue analysis without raising additional exceptions.
    """

    def __init__(self, page):
        self.page = page

    def get_scoped_dom(self, parent_locator: str = None) -> str:
        try:
            if parent_locator:
                return self.page.locator(parent_locator).inner_html()
            return self.page.content()
        except Exception:
            # Return empty string on any failure to keep callers resilient
            return ""

    def find_error_candidates(self, parent_locator: str = None):
        candidates = []

        scope = self.page.locator(parent_locator) if parent_locator else self.page

        # Common selectors to probe for error/alert text within the scope
        selectors = [
            "[role='alert']",
            "[data-test*='error']",
            "[class*='error']",
            ".error-message-container",
            "h3"
        ]

        for selector in selectors:
            try:
                elements = scope.locator(selector).all()
                for el in elements:
                    text = el.inner_text().strip()
                    if text:
                        candidates.append({
                            "selector": selector,
                            "text": text
                        })
            except Exception:
                # If a selector lookup fails for any reason, skip it and
                # continue scanning other selectors.
                continue

        return candidates
