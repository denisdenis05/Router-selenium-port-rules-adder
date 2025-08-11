from selenium import webdriver
from selenium.common import NoAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import time

# ---------------- CONFIG ----------------
ROUTER_URL = "http://192.168.1.1"
USERNAME = "user"
PASSWORD = "password"

# List of rules: (Private IP, Public Port, Private Port)
RULES = [
    ("192.168.1.80", "22", "22"),
    ("192.168.1.80", "80", "80"),
]
# -----------------------------------------

options = Options()
options.add_argument("--headless")

driver = webdriver.Firefox(options=options)


def login():
    """Log into the router."""
    driver.get(f"{ROUTER_URL}/")
    WebDriverWait(driver, 10).until(
        EC.frame_to_be_available_and_switch_to_it((By.NAME, "loginPage"))
    )
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "login_username"))
    )
    driver.find_element(By.ID, "login_username").send_keys(USERNAME)
    driver.find_element(By.ID, "login_password").send_keys(PASSWORD)
    driver.find_element(By.ID, "btn_login_step_1").click()
    time.sleep(2)

    try:
        WebDriverWait(driver, 5).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        print("[!] Alert detected:", alert.text)
        alert.accept()
    except NoAlertPresentException:
        pass


def navigate_to_port_forwarding():
    """Navigate to the Port Forwarding page."""
    driver.switch_to.frame("loginPage")
    driver.find_element(By.ID, "Application").click()
    time.sleep(1)
    driver.find_element(By.ID, "Port Forwarding").click()
    time.sleep(1)
    driver.find_element(By.XPATH, "//div[text()='Port Forwarding']").click()
    time.sleep(2)
    driver.switch_to.default_content()
    driver.switch_to.frame("loginPage")
    driver.switch_to.frame("frameContent")
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "rule_add"))
    )


def rule_exists(ip, ext_port, int_port):
    """Check if a port forwarding rule already exists."""
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "ruleTable"))
    )

    try:
        no_rule_row = driver.find_element(By.ID, "record_no")
        if no_rule_row:
            print("[=] No rules currently in the table.")
            return False
    except:
        pass  # No "record_no" row, so there are rules to check

    rows = driver.find_elements(By.XPATH, "//table[@id='ruleTable']//tr[starts-with(@id, 'record_') and not(@id='record_no')]")

    for row in rows:
        pub_port = row.find_element(By.XPATH, ".//td[contains(@id, 'pm_pubPort_')]").text.strip()
        pri_ip = row.find_element(By.XPATH, ".//td[contains(@id, 'pm_priIP_')]").text.strip()
        pri_port = row.find_element(By.XPATH, ".//td[contains(@id, 'pm_priPort_')]").text.strip()
        enabled = row.find_element(By.XPATH, ".//td[contains(@id, 'pm_enable_')]").text.strip()

        if pub_port == f"{ext_port}-{ext_port}" and pri_ip == ip and pri_port == f"{int_port}-{int_port}" and enabled.lower() == "enable":
            return True

    return False


def add_rule(ip, ext_port, int_port):
    """Add a new port forwarding rule."""
    driver.find_element(By.ID, "rule_add").click()
    print(f"[+] Adding rule: {ext_port} → {ip}:{int_port}")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "pm_pubPortStart"))
    )

    driver.find_element(By.ID, "pm_pubPortStart").clear()
    driver.find_element(By.ID, "pm_pubPortStart").send_keys(ext_port)
    driver.find_element(By.ID, "pm_pubPortEnd").clear()
    driver.find_element(By.ID, "pm_pubPortEnd").send_keys(ext_port)
    driver.find_element(By.ID, "pm_priIP").clear()
    driver.find_element(By.ID, "pm_priIP").send_keys(ip)
    driver.find_element(By.ID, "pm_priPortStart").clear()
    driver.find_element(By.ID, "pm_priPortStart").send_keys(int_port)
    driver.find_element(By.ID, "pm_priPortEnd").clear()
    driver.find_element(By.ID, "pm_priPortEnd").send_keys(int_port)

    enable_dropdown = Select(driver.find_element(By.ID, "pm_enable"))
    enable_dropdown.select_by_value("1")

    driver.find_element(By.ID, "pm_apply").click()
    print("[+] Clicked Apply")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "ruleTable"))
    )


def logout():
    """Log out of the router."""
    driver.switch_to.default_content()
    WebDriverWait(driver, 10).until(
        EC.frame_to_be_available_and_switch_to_it((By.NAME, "loginPage"))
    )
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "headerLogoutSpan"))
    )
    driver.find_element(By.ID, "headerLogoutSpan").click()
    print("[+] Logged out successfully")


# ---------------- MAIN SCRIPT ----------------
try:
    login()
    navigate_to_port_forwarding()

    for ip, ext_port, int_port in RULES:
        if rule_exists(ip, ext_port, int_port):
            print(f"[=] Rule {ext_port} → {ip}:{int_port} already exists. Skipping.")
        else:
            add_rule(ip, ext_port, int_port)
            if rule_exists(ip, ext_port, int_port):
                print(f"[✅] Rule {ext_port} → {ip}:{int_port} added successfully.")
            else:
                print(f"[❌] Failed to add rule {ext_port} → {ip}:{int_port}.")

    logout()

finally:
    driver.quit()