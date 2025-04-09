# conda 사용 시
conda env create environment.yml
- - -
# venv 사용 시
pip install -r requirements.txt
- - -
# 데이터베이스 마이그레이션 하는 법
alembic revision --autogenerate

alembic upgrade head
