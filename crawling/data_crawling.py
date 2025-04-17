import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import os
import time
import requests
from dotenv import load_dotenv
from db.database import SessionLocal
from models.restaurant import Restaurant

load_dotenv()
API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
PLACE_URL = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
DETAIL_URL = "https://maps.googleapis.com/maps/api/place/details/json"

def update_with_google_data():
    db = SessionLocal()
    restaurants = db.query(Restaurant).filter(Restaurant.latitude == None).all()

    for r in restaurants:
        params = {
            'input': f"{r.name} {r.address}",
            'inputtype': 'textquery',
            'fields': 'place_id',
            'key': API_KEY
        }
        res = requests.get(PLACE_URL, params=params).json()
        candidates = res.get('candidates', [])
        if not candidates:
            print(f"❌ 구글에서 식당 못 찾음: {r.name}")
            continue

        place_id = candidates[0]['place_id']
        details_res = requests.get(DETAIL_URL, params={
            'place_id': place_id,
            'fields': 'geometry,rating',
            'key': API_KEY
        }).json()
        result = details_res.get('result', {})

        if 'geometry' in result:
            r.latitude = result['geometry']['location']['lat']
            r.longitude = result['geometry']['location']['lng']
        if 'rating' in result:
            r.rating = result['rating']

        db.commit()
        print(f"✅ {r.name} 업데이트 완료")

    db.close()

if __name__ == "__main__":
    update_with_google_data()
