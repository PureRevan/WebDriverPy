from WebDriverPy import OpenWhatIsMyIP, OpenGoogle, Proxy, WebDriver


def main() -> None:
    """
    :return: Uses the OpenWhatIsMyIP script with proxies set to "auto" and print_logs set to True. Otherwise, default configuration.
    """

    # Proxies here
    p = []

    driver = setup_driver(p)
    try:
        if driver.uses_proxy:
            open_what_is_my_ip(driver)
        else:
            open_google(driver)
    finally:
        driver.quit()


def setup_driver(p: list[str] | list[Proxy] | str | Proxy | None):
    no_cookies = not bool(p)
    proxies = p if p else None

    return WebDriver(print_logs=True, no_cookies=no_cookies, proxies=proxies)


def open_what_is_my_ip(driver: WebDriver) -> None:
    OpenWhatIsMyIP(driver).run()
    driver.wait(10)
    driver.rotate_proxy()
    OpenWhatIsMyIP(driver).run()

    while True:
        driver.wait_for_user_input("Press Enter for next proxy...")
        driver.rotate_proxy()
        OpenWhatIsMyIP(driver).run()


def open_google(driver: WebDriver) -> None:
    OpenGoogle(driver).run()
    driver.wait_for_user_input("Finished...")


def clear_all_downloads():
    WebDriver(late_init=True, print_logs=True).clear_downloads()


def readme_example():
    """
    The example from README.md
    """
    from WebDriverPy import WebDriver

    WebDriver(no_cookies=True) \
        .get("https://google.com") \
        .wait_click_write_submit("Hello World!", "q", by="name") \
        .wait_for_user_input() \
        .quit()


if __name__ == '__main__':
    readme_example()
