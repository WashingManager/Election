from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import os
import sys

# 웹드라이버 설정
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')

def save_empty_file(filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({"error": "No data scraped"}, f, ensure_ascii=False, indent=2)

def scrape_vcap02():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    try:
        url = "http://info.nec.go.kr/main/showDocument.xhtml?electionId=0020250603&topMenuId=VC&secondMenuId=VCAP02"
        print(f"Accessing VCAP02: {url}")
        driver.get(url)
        
        try:
            search_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//input[@type="image" and @alt="검색"]'))
            )
            print("Clicking search button for VCAP02")
            search_button.click()
        except Exception as e:
            print(f"VCAP02 search button error: {e}")
        
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, 'table01'))
        )
        print("Found table01 for VCAP02")
        table = driver.find_element(By.ID, 'table01')
        rows = table.find_elements(By.TAG_NAME, 'tr')
        
        data = []
        for row in rows[1:]:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if cells:
                try:
                    region = cells[0].text.strip()
                    total_voters = int(cells[1].text.replace(',', '').strip())
                    in_region_voters = int(cells[2].text.replace(',', '').strip())
                    out_region_voters = int(cells[3].text.replace(',', '').strip())
                    data.append({
                        "region": region,
                        "totalVoters": total_voters,
                        "inRegionVoters": in_region_voters,
                        "outRegionVoters": out_region_voters
                    })
                except (IndexError, ValueError) as e:
                    print(f"VCAP02 row parsing error: {e}")
                    continue
        
        if data:
            with open('election_data.json', 'w', encoding='utf-8') as f:
                json.dump({"preElectionResults": data}, f, ensure_ascii=False, indent=2)
            print("VCAP02 data saved to election_data.json")
        else:
            print("No VCAP02 data found")
            save_empty_file('election_data.json')
    
    except Exception as e:
        print(f"VCAP02 scraping failed: {e}")
        save_empty_file('election_data.json')
    
    finally:
        driver.quit()

def scrape_vcap01():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    try:
        url = "http://info.nec.go.kr/main/showDocument.xhtml?electionId=0020250603&topMenuId=VC&secondMenuId=VCAP01"
        print(f"Accessing VCAP01: {url}")
        driver.get(url)
        
        try:
            search_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//input[@type="image" and @alt="검색"]'))
            )
            print("Clicking search button for VCAP01")
            search_button.click()
        except Exception as e:
            print(f"VCAP01 search button error: {e}")
        
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, 'table01'))
        )
        print("Found table01 for VCAP01")
        table = driver.find_element(By.ID, 'table01')
        rows = table.find_elements(By.TAG_NAME, 'tr')
        
        data = []
        for row in rows[1:]:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if cells:
                try:
                    region = cells[0].text.strip()
                    electors = int(cells[1].text.replace(',', '').strip())
                    total_voters = int(cells[2].text.replace(',', '').strip())
                    voting_rate = float(cells[3].text.strip())
                    data.append({
                        "region": region,
                        "electors": electors,
                        "totalVoters": total_voters,
                        "votingRate": voting_rate
                    })
                except (IndexError, ValueError) as e:
                    print(f"VCAP01 row parsing error: {e}")
                    continue
        
        if data:
            with open('election_summary.json', 'w', encoding='utf-8') as f:
                json.dump({"electionSummary": data}, f, ensure_ascii=False, indent=2)
            print("VCAP01 data saved to election_summary.json")
        else:
            print("No VCAP01 data found")
            save_empty_file('election_summary.json')
    
    except Exception as e:
        print(f"VCAP01 scraping failed: {e}")
        save_empty_file('election_summary.json')
    
    finally:
        driver.quit()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "vcap02":
            scrape_vcap02()
        elif sys.argv[1] == "vcap01":
            scrape_vcap01()
    else:
        print("Please specify 'vcap02' or 'vcap01' as argument")
