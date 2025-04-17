import sys
import os
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.database import SessionLocal
from models.restaurant import Restaurant

def normalize(text):
    return re.sub(r"\s+", "", text.strip().lower())

def crawl_kakao_and_insert(query="경기대학교 맛집", max_pages=5):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.get("https://map.kakao.com/")
    time.sleep(2)

    search_box = driver.find_element(By.ID, "search.keyword.query")
    search_box.send_keys(query)
    search_box.send_keys(Keys.ENTER)
    time.sleep(2)

    # 장소 탭 클릭
    try:
        driver.find_element(By.XPATH, '//*[@id="info.main.options"]/li[2]/a').click()
        time.sleep(2)
    except:
        pass

    db = SessionLocal()

    def parse_page():
        soup = BeautifulSoup(driver.page_source, "html.parser")
        places = soup.select("li.PlaceItem")
        for place in places:
            try:
                name = place.select_one(".head_item .tit_name .link_name").text.strip()
                score_tag = place.select_one(".rating .score em")
                score = float(score_tag.text.strip()) if score_tag else None
                addr_tag = place.select_one(".info_item .addr p")
                address = addr_tag.text.strip() if addr_tag else ""

                print(f"🏷 {name} | ⭐ {score} | 📍 {address}")

                exists = db.query(Restaurant).filter(
                    Restaurant.name == name,
                    Restaurant.address == address
                ).first()

                if not exists:
                    r = Restaurant(name=name, address=address, kakao_rating=score)
                    db.add(r)
                    db.commit()
                    print("✅ DB에 새 식당 저장 완료")
                else:
                    print("⚠️ 이미 존재하는 식당")

            except Exception as e:
                print(f"[!] 파싱 오류: {e}")

    print("🔎 [1페이지]")
    parse_page()

    # 2페이지 진입용 '더보기' 버튼
    try:
        more_button = driver.find_element(By.ID, "info.search.place.more")
        driver.execute_script("arguments[0].click();", more_button)
        time.sleep(2)
        print("🔎 [2페이지]")
        parse_page()
    except:
        print("❌ 더보기 버튼 클릭 실패")

    # 3페이지 이후부터는 페이지 번호 클릭
    for page in range(3, max_pages + 1):
        print(f"🔎 [{page}페이지]")
        try:
            next_button = driver.find_element(By.ID, f"info.search.page.no{page}")
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(2)
            parse_page()
        except:
            print(f"❌ {page}페이지 없음 또는 클릭 실패")
            break

    db.close()
    driver.quit()

if __name__ == "__main__":
    crawl_kakao_and_insert()
