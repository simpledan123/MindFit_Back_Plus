import sys
import os
import time
import requests
from dotenv import load_dotenv
from db.database import SessionLocal
from models.restaurant import Restaurant
from sqlalchemy.orm import Session

# .env 파일 로드
load_dotenv()

# 구글 맵 API 키
API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
NEARBY_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"

# 위치 설정
LOCATION = "37.2964,127.0097"  # 경기대학교
RADIUS = 1000  # 1km

# 공백 문자 정리
def clean_whitespace(text):
    if text:
        text = text.replace('\u2009', ' ').replace('\u202f', ' ')
    return text

# Nearby Search (식당 리스트 가져오기)
def get_nearby_restaurants(location, radius):
    all_results = []
    params = {
        'key': API_KEY,
        'location': location,
        'radius': radius,
        'type': 'restaurant'
    }

    while True:
        response = requests.get(NEARBY_SEARCH_URL, params=params)
        result = response.json()

        print(result)

        all_results.extend(result.get('results', []))

        next_page_token = result.get('next_page_token')
        if next_page_token:
            time.sleep(2)
            params = {
                'key': API_KEY,
                'pagetoken': next_page_token
            }
        else:
            break

    return all_results

# Details API (상세 정보 가져오기)
def get_place_details(place_id):
    params = {
        'key': API_KEY,
        'place_id': place_id,
        'fields': 'name,formatted_address,geometry,formatted_phone_number,opening_hours,website'
    }
    response = requests.get(DETAILS_URL, params=params)
    return response.json().get('result', {})

# DB 저장
def save_to_db(restaurants):
    db: Session = SessionLocal()

    for restaurant in restaurants:
        place_id = restaurant['place_id']
        details = get_place_details(place_id)

        db_restaurant = Restaurant(
            name=clean_whitespace(details.get('name')),
            address=clean_whitespace(details.get('formatted_address')),
            latitude=details['geometry']['location']['lat'] if 'geometry' in details else None,
            longitude=details['geometry']['location']['lng'] if 'geometry' in details else None,
            phone=details.get('formatted_phone'),
            opening_hours=', '.join(details['opening_hours']['weekday_text']) if 'opening_hours' in details else None,
            place_id=restaurant.get('place_id')
        )

        db.add(db_restaurant)
        db.commit()
        db.refresh(db_restaurant)

    db.close()

# 메인 실행
if __name__ == "__main__":
    restaurants = get_nearby_restaurants(LOCATION, RADIUS)
    print(f"식당 {len(restaurants)}개 찾음. DB에 저장 시작.")
    save_to_db(restaurants)
    print("모든 식당 저장 완료.")
