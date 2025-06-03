from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
from datetime import datetime

# 웹드라이버 설정
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    # VCVP01 페이지 데이터 스크래핑
    url = "http://info.nec.go.kr/main/showDocument.xhtml?electionId=0020250603&topMenuId=VC&secondMenuId=VCVP01"
    driver.get(url)

    search_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//input[@type="image" and @alt="검색"]'))
    )
    search_button.click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'table01'))
    )

    table = driver.find_element(By.ID, 'table01')
    rows = table.find_elements(By.TAG_NAME, 'tr')

    data = []
    for row in rows[1:]:  # 헤더 제외
        cells = row.find_elements(By.TAG_NAME, 'td')
        if cells:
            try:
                region = cells[0].text.strip()
                election_day_voters = int(cells[1].text.replace(',', '').strip())
                early_mail_voters = int(cells[2].text.replace(',', '').strip())
                total_electors = int(cells[3].text.replace(',', '').strip())
                election_day_votes = int(cells[4].text.replace(',', '').strip())
                early_mail_votes = int(cells[5].text.replace(',', '').strip())
                total_votes = int(cells[6].text.replace(',', '').strip())
                voting_rate = float(cells[7].text.strip('%'))
                data.append({
                    "region": region,
                    "electionDayVoters": election_day_voters,
                    "earlyMailVoters": early_mail_voters,
                    "totalElectors": total_electors,
                    "electionDayVotes": election_day_votes,
                    "earlyMailVotes": early_mail_votes,
                    "totalVotes": total_votes,
                    "votingRate": voting_rate
                })
            except (IndexError, ValueError) as e:
                print(f"Row parsing error (VCVP01): {e}")
                continue

    # 현재 UTC 시간 기록
    last_updated = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    # JSON 데이터에 lastUpdated 추가
    output_data = {
        "lastUpdated": last_updated,
        "votingProgress": data
    }

    with open('voting_progress.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"VCVP01 데이터가 voting_progress.json 파일로 저장되었습니다. (마지막 업데이트: {last_updated})")

except Exception as e:
    print(f"Error occurred: {e}")

finally:
    driver.quit()
