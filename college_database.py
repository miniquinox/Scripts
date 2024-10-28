import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scraping():
    # Initialize Selenium WebDriver with headless mode and optimizations
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")  # Disables GPU hardware acceleration, useful in headless mode
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model

    # Bypass SSL certificate errors
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--allow-insecure-localhost")
    chrome_options.add_argument("--ignore-ssl-errors")

    # Use the ChromeDriver located on your Desktop
    service = Service("/Users/miniquinox/Desktop/chromedriver")  # Update path to match the location of your chromedriver
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Start tracking time
    start_time = time.time()

    # Open the URL
    url = "https://www.univstats.com/salary/?search=true&school-name="
    driver.get(url)

    # Create a WebDriverWait object to wait for elements
    wait = WebDriverWait(driver, 10)  # Reduced wait time for performance

    # Create a CSV file to store the data
    with open("college_database.csv", mode="w", newline="", encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["College Name", "College URL", "Faculty", "Average Faculty Salary"])

        while True:
            try:
                # Wait until the schoolboxwrap element is visible
                schoolbox_wrap = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "schoolboxwrap")))

                # Get all schoolbox elements inside the schoolboxwrap
                school_boxes = schoolbox_wrap.find_elements(By.CLASS_NAME, "schoolbox")
                print(f"Found {len(school_boxes)} school boxes on the page.")  # Debugging print

                for index, school_box in enumerate(school_boxes):
                    try:
                        # Extract the College Name and URL
                        college_name = school_box.find_element(By.TAG_NAME, "h3").text
                        college_url = school_box.find_element(By.TAG_NAME, "a").get_attribute("href")

                        # Extract faculty and salary info with fallback for missing data
                        try:
                            faculty = school_box.find_element(By.XPATH, ".//span[contains(text(),'Number of Full-time Faculty')]/following-sibling::span").text
                        except:
                            faculty = "<Unknown>"

                        try:
                            avg_faculty_salary = school_box.find_element(By.XPATH, ".//span[contains(text(),'Average Faculty Salary')]/following-sibling::span").text
                        except:
                            avg_faculty_salary = "<Unknown>"

                        # Write the data to the CSV file
                        csv_writer.writerow([college_name, college_url, faculty, avg_faculty_salary])

                        # Print the data to console (for debugging)
                        print(f"College Name: {college_name}, URL: {college_url}, Faculty: {faculty}, Avg Faculty Salary: {avg_faculty_salary}")

                    except Exception as e:
                        print(f"Error processing school box {index + 1}: {e}")  # Debugging print for errors

                # Check if a next button exists and navigate to the next page
                try:
                    next_button = driver.find_element(By.CLASS_NAME, "next")
                    next_page_link = next_button.find_element(By.TAG_NAME, "a").get_attribute("href")

                    # Navigate to the next page
                    print("Navigating to the next page...")  # Debugging print
                    driver.get(next_page_link)
                    time.sleep(1)  # Reduced wait time to speed up performance
                except Exception as e:
                    print(f"No more pages or error occurred: {e}")
                    break

            except Exception as e:
                print(f"Error occurred while loading page: {e}")
                break

    # Close the browser after scraping is complete
    driver.quit()

    # End time
    end_time = time.time()

    # Calculate and print elapsed time
    elapsed_time = end_time - start_time
    minutes, seconds = divmod(elapsed_time, 60)
    print(f"Total time elapsed: {int(minutes)} minutes and {int(seconds)} seconds")


def cleanup():

    # Define input and output file paths
    input_file = "college_database.csv"  # Input CSV file
    output_file = "college_database_cleaned.csv"  # Output cleaned CSV file

    # Open the input CSV file for reading
    with open(input_file, mode="r", encoding="utf-8") as infile:
        csv_reader = csv.reader(infile)
        header = next(csv_reader)  # Read the header row

        # Open the output CSV file for writing
        with open(output_file, mode="w", newline="", encoding="utf-8") as outfile:
            csv_writer = csv.writer(outfile)
            csv_writer.writerow(header)  # Write the header row to the output file

            # Process each row
            for row in csv_reader:
                faculty = row[2]
                salary = row[3]

                # Check if both faculty and salary are not "<Unknown>"
                if faculty != "<Unknown>" and salary != "<Unknown>":
                    csv_writer.writerow(row)  # Write the row if valid

    print(f"Cleaned CSV saved as {output_file}")


if __name__ == "__main__":
    scraping()
    cleanup()