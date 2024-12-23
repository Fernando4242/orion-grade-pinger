from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time
from pprint import pprint
import requests
import os

ORION_USERNAME = os.environ['ORION_USERNAME']
ORION_PASSWORD = os.environ['ORION_PASSWORD']
WEBHOOK_URL = os.environ['WEBHOOK_URL']
TERM_TO_SEARCH = os.environ['TERM_TO_SEARCH']


def get_all_cells_text(driver):
    # Find all rows
    table = driver.find_element(By.TAG_NAME, "table")
    rows = table.find_elements(By.CLASS_NAME, "ps_grid-row")
    data = []

    print(f"Found {len(rows)} rows in the table.")

    for row in rows:
        # Find all td cells in the row
        cells = row.find_elements(By.TAG_NAME, "td")
        # Extract text from each cell and strip any extra whitespace
        row_data = [cell.text.strip() for cell in cells]
        # Add row data to the overall list
        data.append(row_data)

    print(f"Extracted {len(data)} rows of data.")
    return data


def get_changed_data(current_data, previous_data):
    """
    Compare current data with previous data and return the rows that have changed.
    """
    if previous_data is None:
        print("Previous data is None. No changes to compare.")
        return []

    changed_rows = []
    print("Comparing current data with previous data...")

    # Compare current_data with previous_data
    for current_row, previous_row in zip(current_data, previous_data):
        # Check if any field is different
        if current_row != previous_row:
            changed_rows.append(current_row)

    print(f"Found {len(changed_rows)} changed rows.")
    return changed_rows


def format_course_data(courses):
    formatted_message = "### New Data Fetched from Orion Web Portal\n\n"
    formatted_message += "Here are the latest updates:\n\n"

    print("Formatting course data for message.")

    for course in courses:
        formatted_message += f"**Course:** {course[0]}\n"
        formatted_message += f"**Description:** {course[1]}\n"
        formatted_message += f"**Term:** {course[2]}\n"
        formatted_message += f"**Grade:** {course[3]}\n"
        formatted_message += f"**Credits:** {course[4]}\n"
        formatted_message += f"**Status:** {course[5]}\n"
        formatted_message += "----------------------------\n"

    return formatted_message


if __name__ == '__main__':
    print("Creating webdriver...")
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--ignore-ssl-errors=yes")
    chrome_options.add_argument("--ignore-certificate-errors")

    driver = webdriver.Remote(
        command_executor="http://selenium:4444",
        options=chrome_options
    )
    print("WebDriver created successfully.")

    try:
        print("Accessing Orion Web portal...")
        # login into the portal
        driver.get("https://www.utdallas.edu/galaxy/")
        driver.find_element(By.LINK_TEXT, "Orion").click()
        print("Navigating to Orion...")

        driver.find_element(By.ID, "netid").send_keys(ORION_USERNAME)
        driver.find_element(By.ID, "password").send_keys(ORION_PASSWORD)
        driver.find_element(By.ID, "submit").click()
        print("Logging in with provided credentials.")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "trust-browser-button"))
        )
        print("Trust browser button found, clicking...")
        driver.find_element(By.ID, "trust-browser-button").click()

        print("Waiting for URL change...")
        while driver.current_url.find("dacs-prd.utshare.utsystem.edu") == -1:
            pass

        print("Navigated to the expected URL.")
        time.sleep(3)
        driver.find_element(By.ID, "HOMEPAGE_SELECTOR$PIMG").click()
        print("Clicked on the homepage selector.")
        time.sleep(5)
        driver.find_element(By.ID, "PTNUI_SELLP_DVW_PTNUI_LP_NAME$1").click()
        print("Clicked on PTNUI_SellP...")
        time.sleep(5)
        driver.find_element(By.ID, "win0divPTNUI_LAND_REC_GROUPLET$2").click()
        print("Clicked on win0divPTNUI_LAND_REC_GROUPLET.")
        time.sleep(5)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )

        previous_data = None  # Initialize previous_data to None
        print("Starting data pull loop...")

        while True:
            print("#########\n PULLING LATEST INFORMATION #########")
            cell_data = get_all_cells_text(driver)
            filtered = list(filter(lambda x: len(x) > 2 and x[2] == TERM_TO_SEARCH, cell_data))
            print(f"Filtered data for {TERM_TO_SEARCH}: {len(filtered)} rows.")

            if previous_data is None:
                print("No previous data, sending first data pull...")
                requests.post(
                    WEBHOOK_URL,
                    json={
                        "content": format_course_data(filtered)
                    })
                print("Data posted to Discord.")

            # Print the changed rows if any changes are detected
            changed_rows = get_changed_data(filtered, previous_data)
            if changed_rows:
                print("#########\n CHANGES DETECTED #########")
                pprint(changed_rows)
                requests.post(
                    WEBHOOK_URL,
                    json={
                        "content": format_course_data(filtered)
                    })
                print("Changes posted to Discord.")

            # Update previous_data to the current filtered data
            previous_data = filtered
            print("Previous data updated.")

            time.sleep(150)  # Wait for 2 minutes before refreshing
            print("Refreshing the page...")
            driver.refresh()
            time.sleep(150)  # Wait for 3 minutes to ensure page is loaded
            driver.refresh()
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            print("Page refreshed and ready.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        driver.quit()  # Ensure the driver is closed after the error
        print("WebDriver closed due to error.")
