import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests
from db.database import SessionLocal
from models.restaurant import Restaurant
from models.menu import Menu
from models.keyword import Keyword, menu_keywords
from sqlalchemy.orm import Session

# 구글 맵 API 설정
API_KEY = '여기에 당신의 키를 입력하세용'
NEARBY_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"

# 경기대학교 위치
LOCATION = "37.2390,127.0100"
RADIUS = 1500 #1500미터 반경

def clean_whitespace(text):
    if text:
        text = text.replace('\u2009', ' ')
        text = text.replace('\u202f', ' ')
    return text

def get_nearby_restaurants(location, radius=RADIUS):
    params = {
        'key': API_KEY,
        'location': location,
        'radius': radius,
        'type': 'restaurant'
    }
    response = requests.get(NEARBY_SEARCH_URL, params=params)
    if response.status_code == 200:
        return response.json().get('results', [])
    else:
        print("Error in Nearby Search:", response.status_code)
        return []

def get_place_details(place_id):
    params = {
        'key': API_KEY,
        'place_id': place_id,
        'fields': 'name,formatted_phone_number,opening_hours,rating'
    }
    response = requests.get(DETAILS_URL, params=params)
    if response.status_code == 200:
        return response.json().get('result', {})
    else:
        print("Error in Place Details:", response.status_code)
        return {}

def save_to_db(db: Session, restaurant_data):
    db_restaurant = Restaurant(
        name=restaurant_data['name'],
        phone=restaurant_data['phone'],
        rating=restaurant_data['rating'],
        address="경기대학교 근처",
        latitude=37.2390,
        longitude=127.0100,
        place_id=restaurant_data['place_id'],
        opening_hours=restaurant_data['opening_hours']
    )
    db.add(db_restaurant)
    db.commit()
    db.refresh(db_restaurant)

    # 기본 메뉴 추가
    default_menu = Menu(
        restaurant_id=db_restaurant.id,
        menu_item="메뉴 없음",
        price="0"
    )
    db.add(default_menu)
    db.commit()
    db.refresh(default_menu)

    # 기본 키워드 연결
    default_keyword = db.query(Keyword).filter(Keyword.keyword == "기본").first()
    if not default_keyword:
        default_keyword = Keyword(keyword="기본")
        db.add(default_keyword)
        db.commit()
        db.refresh(default_keyword)

    db.execute(menu_keywords.insert().values(menu_id=default_menu.id, keyword_id=default_keyword.id))
    db.commit()

def main():
    db = SessionLocal()

    restaurants = get_nearby_restaurants(LOCATION)

    for restaurant in restaurants:
        place_id = restaurant.get('place_id')
        details = get_place_details(place_id)

        opening_hours = ''
        if details.get('opening_hours'):
            weekday_text = details.get('opening_hours', {}).get('weekday_text', [])
            weekday_text = [clean_whitespace(text) for text in weekday_text]
            opening_hours = ', '.join(weekday_text)

        restaurant_data = {
            'place_id': place_id,
            'name': details.get('name') or restaurant.get('name'),
            'rating': details.get('rating') or restaurant.get('rating'),
            'phone': details.get('formatted_phone_number', ''),
            'opening_hours': opening_hours
        }

        save_to_db(db, restaurant_data)

    db.close()
    print("✅ 크롤링 및 DB 저장 완료되었습니다.")
    print(f"크롤링된 식당 수: {len(restaurants)}")

if __name__ == "__main__":
    main()
