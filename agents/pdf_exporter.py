from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import base64
import json
import os

def save_html_to_pdf(html_file_path, pdf_path):
    driver = None
    try:
        print(f"[INFO] Generating PDF report at {pdf_path}")
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=chrome_options)
        
        absolute_html_path = f"file:///{os.path.abspath(html_file_path)}"
        driver.get(absolute_html_path)

        print_options = {
            'printBackground': True,
            'paperWidth': 8.5,
            'paperHeight': 11,
            'marginTop': 0.5,
            'marginBottom': 0.5,
            'marginLeft': 0.5,
            'marginRight': 0.5
        }
        result = driver.execute_cdp_cmd("Page.printToPDF", print_options)
        
        pdf_data = base64.b64decode(result['data'])
        with open(pdf_path, "wb") as f:
            f.write(pdf_data)
            
        print(f"[SUCCESS] PDF report saved successfully.")
        return True
    except Exception as e:
        print(f"[ERROR] Could not generate PDF: {e}")
        return False
    finally:
        if driver:
            driver.quit()