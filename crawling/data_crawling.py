import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from dotenv import load_dotenv
from db.database import SessionLocal
from models.restaurant import Restaurant
from models.menu import Menu
from models.keyword import Keyword, menu_keywords
from sqlalchemy.orm import Session

# .env 파일 로드
load_dotenv()

# 구글 맵 API 설정
API_KEY = os.getenv('GOOGLE_API_KEY')
NEARBY_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"


# 경기대학교 위치
LOCATION = "37.2390,127.0100"
RADIUS = 1500  # 1.5km 반경

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
        'fields': 'name,formatted_phone_number,opening_hours,rating,geometry'
    }
    response = requests.get(DETAILS_URL, params=params)
    if response.status_code == 200:
        return response.json().get('result', {})
    else:
        print("Error in Place Details:", response.status_code)
        return {}

def save_to_db(db: Session, restaurant_data):
    # 식당 데이터 저장
    db_restaurant = Restaurant(
        name=restaurant_data['name'],
        phone=restaurant_data['phone'],
        rating=restaurant_data['rating'],
        address=restaurant_data['address'],
        latitude=restaurant_data['latitude'],
        longitude=restaurant_data['longitude'],
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

        # place_id 중복 체크
        exists = db.query(Restaurant).filter(Restaurant.place_id == place_id).first()
        if exists:
            print(f"⚡ 이미 저장된 place_id: {place_id}, 스킵합니다.")
            continue

        details = get_place_details(place_id)

        if not details:
            continue

        location_info = details.get('geometry', {}).get('location', {})
        latitude = location_info.get('lat')
        longitude = location_info.get('lng')

        if not (latitude and longitude):
            print(f"⚠️ 위도/경도 정보 없음: {place_id}, 스킵합니다.")
            continue

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
            'address': restaurant.get('vicinity', '주소 정보 없음'),
            'latitude': latitude,
            'longitude': longitude,
            'opening_hours': opening_hours
        }

        save_to_db(db, restaurant_data)

    db.close()
    print("✅ 크롤링 및 DB 저장 완료되었습니다.")
    print(f"크롤링된 식당 수: {len(restaurants)}")

if __name__ == "__main__":
    main()
