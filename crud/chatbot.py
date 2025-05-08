
from sqlalchemy.orm import Session
from models.chatbot import UserSummary, UserKeyword

def get_user_summary(db: Session, user_id: int):
    return db.query(UserSummary).filter(UserSummary.user_id == user_id).first()

def save_user_summary(db: Session, user_id: int, summary: str):
    existing = get_user_summary(db, user_id)
    if existing:
        existing.summary = summary
    else:
        existing = UserSummary(user_id=user_id, summary=summary)
        db.add(existing)
    db.commit()
    return existing

def save_user_keywords(db: Session, user_id: int, keywords: list[str]):
    for kw in keywords:
        entry = db.query(UserKeyword).filter_by(user_id=user_id, keyword=kw).first()
        if entry:
            entry.count += 1
        else:
            entry = UserKeyword(user_id=user_id, keyword=kw, count=1)
            db.add(entry)
    db.commit()
