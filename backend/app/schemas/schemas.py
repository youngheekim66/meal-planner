"""
Pydantic schemas for request/response
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from enum import Enum


# ─── Enums ─────────────────────
class SexType(str, Enum):
    M = "M"
    F = "F"

class CuisineType(str, Enum):
    KOREAN = "KOREAN"
    FREE = "FREE"

class MealType(str, Enum):
    BREAKFAST = "BREAKFAST"
    LUNCH = "LUNCH"
    DINNER = "DINNER"


# ─── User ──────────────────────
class UserCreate(BaseModel):
    name: str
    birth_year: Optional[int] = None
    sex: Optional[SexType] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    activity_level: int = 2

class UserPreferenceUpdate(BaseModel):
    disliked_ingredients: list[int] = []
    allergies: list[str] = []
    meals_per_day: int = 3
    kcal_target: Optional[int] = None

class UserOut(BaseModel):
    id: int
    name: str
    birth_year: Optional[int]
    sex: Optional[str]
    height_cm: Optional[float]
    weight_kg: Optional[float]
    activity_level: int
    kcal_target: Optional[int] = None

    class Config:
        from_attributes = True


# ─── Ingredient ────────────────
class IngredientOut(BaseModel):
    id: int
    name_std: str
    category: Optional[str]
    default_unit: str

    class Config:
        from_attributes = True


# ─── Recipe ────────────────────
class RecipeIngredientOut(BaseModel):
    ingredient: IngredientOut
    qty: float
    unit: str
    qty_in_grams: Optional[float]
    note: Optional[str]

    class Config:
        from_attributes = True

class RecipeOut(BaseModel):
    id: int
    title: str
    cuisine: str
    tags: list[str]
    meal_types: list[str]
    difficulty: int
    cook_time_min: int
    servings: int
    steps: list[dict]
    source_type: str
    source_url: Optional[str]
    thumbnail_url: Optional[str]
    youtube_url: Optional[str] = None    # ← 이 줄 추가
    kcal_per_serving: Optional[float] = None
    macros_per_serving: Optional[dict] = None

    class Config:
        from_attributes = True

class RecipeCreate(BaseModel):
    title: str
    cuisine: CuisineType = CuisineType.KOREAN
    tags: list[str] = []
    meal_types: list[str] = ["LUNCH", "DINNER"]
    difficulty: int = 2
    cook_time_min: int = 30
    servings: int = 2
    steps: list[dict] = []
    source_type: str = "MANUAL"
    source_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    ingredients: list[dict] = []  # [{"ingredient_id":1,"qty":100,"unit":"g","note":""}]


# ─── Menu Plan ─────────────────
class MenuPlanItemOut(BaseModel):
    id: int
    date: date
    meal_type: str
    recipe: RecipeOut
    servings_for_user: float
    kcal_est: Optional[float]
    macros_est: Optional[dict]

    class Config:
        from_attributes = True

class MenuPlanOut(BaseModel):
    id: int
    week_start: date
    rotation_key: str
    items: list[MenuPlanItemOut]
    total_kcal: Optional[float] = None
    daily_summary: Optional[list[dict]] = None

    class Config:
        from_attributes = True

class MenuPlanGenerate(BaseModel):
    user_id: int
    week_start: date  # 월요일 날짜


# ─── Shopping List ─────────────
class ShoppingListItemOut(BaseModel):
    id: int
    ingredient: IngredientOut
    total_qty: float
    unit: str
    is_pantry: bool
    checked: bool
    note: Optional[str]

    class Config:
        from_attributes = True

class ShoppingListOut(BaseModel):
    id: int
    menu_plan_id: int
    items: list[ShoppingListItemOut]
    categories: Optional[dict] = None  # {"채소": [...], "육류": [...]}

    class Config:
        from_attributes = True

class ShoppingItemCheck(BaseModel):
    item_id: int
    checked: bool


# ─── Nutrition ─────────────────
class NutritionSummary(BaseModel):
    kcal: float = 0
    carb_g: float = 0
    protein_g: float = 0
    fat_g: float = 0
    sodium_mg: float = 0
    calculable: bool = True
    missing_ingredients: list[str] = []
    includes_rice: bool = False


# ─── TDEE 계산 ─────────────────
class TDEERequest(BaseModel):
    sex: SexType
    age: int
    height_cm: float
    weight_kg: float
    activity_level: int = 2  # 1(비활동)~5(매우활동)

class TDEEResponse(BaseModel):
    bmr: float
    tdee: float
    recommended_kcal: float
    breakdown: dict  # {"breakfast": ..., "lunch": ..., "dinner": ...}


# ─── Auth (인증) ──────────────────
class SignupRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=100, examples=["user@example.com"])
    password: str = Field(..., min_length=4, max_length=100, examples=["1234"])
    name: str = Field(..., min_length=1, max_length=50, examples=["홍길동"])
    birth_year: Optional[int] = None
    sex: Optional[SexType] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    activity_level: int = 2

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"

class MeResponse(BaseModel):
    id: int
    email: Optional[str]
    name: str
    birth_year: Optional[int]
    sex: Optional[str]
    height_cm: Optional[float]
    weight_kg: Optional[float]
    activity_level: int
    kcal_target: Optional[int] = None

    class Config:
        from_attributes = True
