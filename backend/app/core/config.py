import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "식단플래너 API"
    VERSION: str = "1.2.0"
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@db:5432/meal_planner")
    FOOD_NUTRIENT_API_KEY: str = ""
    FOOD_NUTRIENT_API_URL: str = "https://apis.data.go.kr/1471000/FoodNtrCpntDbInfo01/getFoodNtrCpntDbInq01"

    # JWT 인증
    JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY", "meal-planner-secret-key-change-in-production-2026")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7일

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()