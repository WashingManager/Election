from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import os

# 웹드라이버 설정
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')  # GPU 비활성화로 안정성 향상
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def save_empty_file(filename):
    """빈 JSON 파일 저장"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({"error": "No data scraped"}, f, ensure_ascii=False, indent=2)

try:
    # VCAP02 데이터 스크래핑
    url1 = "http://info.nec.go.kr/main/showDocument.xhtml?electionId=0020250603&topMenuId=VC&secondMenuId=VCAP02"
    driver.get(url1)
    
    try:
        search_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@type="image" and @alt="검색"]'))
        )
        search_button.click()
    except Exception as e:
        print(f"VCAP02 검색 버튼 클릭 실패: {e}")
    
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, 'table01'))
    )
    table1 = driver.find_element(By.ID, 'table01')
    rows1 = table1.find_elements(By.TAG_NAME, 'tr')
    
    data1 = []
    for row in rows1[1:]:  # 헤더 제외
        cells = row.find_elements(By.TAG_NAME, 'td')
        if cells:
            try:
                region = cells[0].text.strip()
                total_voters = int(cells[1].text.replace(',', ''))
                in_region_voters = int(cells[2].text.replace(',', ''))
                out_region_voters = int(cells[3].text.replace(',', ''))
                data1.append({
                    "region": region,
                    "totalVoters": total_voters,
                    "inRegionVoters": in_region_voters,
                    "outRegionVoters": out_region_voters
                })
            except (IndexError, ValueError) as e:
                print(f"VCAP02 Row parsing error: {e}")
                continue
    
    if data1:
        with open('election_data.json', 'w', encoding='utf-8') as f:
            json.dump({"preElectionResults": data1}, f, ensure_ascii=False, indent=2)
        print("VCAP02 데이터가 election_data.json 파일로 저장되었습니다.")
    else:
        print("VCAP02 데이터가 없습니다.")
        save_empty_file('election_data.json')

    # VCAP01 데이터 스크래핑
    url2 = "http://info.nec.go.kr/main/showDocument.xhtml?electionId=0020250603&topMenuId=VC&secondMenuId=VCAP01"
    driver.get(url2)
    
    try:
        # 페이지가 완전히 로드될 때까지 대기
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, 'table01'))
        )
        table2 = driver.find_element(By.ID, 'table01')
        rows2 = table2.find_elements(By.TAG_NAME, 'tr')
        
        data2 = []
        for row in rows2[1:]:  # 헤더 제외
            cells = row.find_elements(By.TAG_NAME, 'td')
            if cells:
                try:
                    region = cells[0].text.strip()
                    electors = int(cells[1].text.replace(',', '').strip())
                    total_voters = int(cells[2].text.replace(',', '').strip())
                    voting_rate = float(cells[3].text.strip())
                    data2.append({
                        "region": region,
                        "electors": electors,
                        "totalVoters": total_voters,
                        "votingRate": voting_rate
                    })
                except (IndexError, ValueError) as e:
                    print(f"VCAP01 Row parsing error: {e}")
                    continue
        
        if data2:
            with open('election_summary.json', 'w', encoding='utf-8') as f:
                json.dump({"electionSummary": data2}, f, ensure_ascii=False, indent=2)
            print("VCAP01 데이터가 election_summary.json 파일로 저장되었습니다.")
        else:
            print("VCAP01 데이터가 없습니다.")
            save_empty_file('election_summary.json')
    
    except Exception as e:
        print(f"VCAP01 스크래핑 실패: {e}")
        save_empty_file('election_summary.json')

except Exception as e:
    print(f"전체 스크래핑 실패: {e}")
    if not os.path.exists('election_data.json'):
        save_empty_file('election_data.json')
    if not os.path.exists('election_summary.json'):
        save_empty_file('election_summary.json')

finally:
    driver.quit()
