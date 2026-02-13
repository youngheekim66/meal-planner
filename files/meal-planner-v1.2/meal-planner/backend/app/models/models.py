"""
식단 플래너 DB 모델 (ERD 기반)
- users, user_preferences
- recipes, ingredients, recipe_ingredients
- food_nutrients, ingredient_nutrient_map
- menu_plans, menu_plan_items
- shopping_lists, shopping_list_items
"""
from datetime import date, datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Date, DateTime,
    Text, ForeignKey, JSON, Enum as SQLEnum, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


# ─── Enums ───────────────────────────────────────────
class SexType(str, enum.Enum):
    M = "M"
    F = "F"


class CuisineType(str, enum.Enum):
    KOREAN = "KOREAN"
    FREE = "FREE"


class MealType(str, enum.Enum):
    BREAKFAST = "BREAKFAST"
    LUNCH = "LUNCH"
    DINNER = "DINNER"


class SourceType(str, enum.Enum):
    YOUTUBE = "YOUTUBE"
    WEB = "WEB"
    MANUAL = "MANUAL"


class MatchMethod(str, enum.Enum):
    AUTO = "AUTO"
    MANUAL = "MANUAL"


# ─── Users ───────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=True)  # 로그인용
    hashed_password = Column(String(200), nullable=True)                  # bcrypt 해시
    name = Column(String(50), nullable=False)
    birth_year = Column(Integer)
    sex = Column(SQLEnum(SexType))
    height_cm = Column(Float)
    weight_kg = Column(Float)
    activity_level = Column(Integer, default=2)  # 1~5
    created_at = Column(DateTime, default=datetime.utcnow)

    preferences = relationship("UserPreference", back_populates="user", uselist=False)
    menu_plans = relationship("MenuPlan", back_populates="user")


class UserPreference(Base):
    __tablename__ = "user_preferences"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    disliked_ingredients = Column(JSON, default=list)   # [ingredient_id, ...]
    allergies = Column(JSON, default=list)               # ["견과류", "갑각류", ...]
    meals_per_day = Column(Integer, default=3)
    kcal_target = Column(Integer, nullable=True)         # null이면 자동계산

    user = relationship("User", back_populates="preferences")


# ─── Recipes ─────────────────────────────────────────
class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    cuisine = Column(SQLEnum(CuisineType), default=CuisineType.KOREAN)
    tags = Column(JSON, default=list)          # ["국", "찌개", "볶음", ...]
    meal_types = Column(JSON, default=list)    # ["BREAKFAST","LUNCH","DINNER"]
    difficulty = Column(Integer, default=2)     # 1~3
    cook_time_min = Column(Integer, default=30)
    servings = Column(Integer, default=2)
    steps = Column(JSON, default=list)          # [{"step":1,"text":"..."}, ...]
    source_type = Column(SQLEnum(SourceType), default=SourceType.MANUAL)
    source_url = Column(String(500), nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    recipe_ingredients = relationship("RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")


# ─── Ingredients (표준 재료 사전) ────────────────────
class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name_std = Column(String(100), nullable=False, unique=True)  # "대파"
    category = Column(String(50))    # 채소/육류/해산물/양념/유제품/곡류/기타
    default_unit = Column(String(20), default="g")
    density_g_per_ml = Column(Float, nullable=True)
    avg_weight_per_piece_g = Column(Float, nullable=True)  # "대파 1대 ≈ 60g"
    aliases = Column(JSON, default=list)  # ["쪽파","실파"]
    created_at = Column(DateTime, default=datetime.utcnow)

    recipe_ingredients = relationship("RecipeIngredient", back_populates="ingredient")
    nutrient_map = relationship("IngredientNutrientMap", back_populates="ingredient", uselist=False)


# ─── Recipe-Ingredient 매핑 ──────────────────────────
class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), nullable=False)
    qty = Column(Float, nullable=False)        # 숫자
    unit = Column(String(20), default="g")     # g/ml/개/큰술/작은술/컵
    qty_in_grams = Column(Float, nullable=True)  # 정규화된 g 값
    note = Column(String(200), nullable=True)   # "다진 것", "선택"

    recipe = relationship("Recipe", back_populates="recipe_ingredients")
    ingredient = relationship("Ingredient", back_populates="recipe_ingredients")

    __table_args__ = (
        Index("ix_ri_recipe", "recipe_id"),
        Index("ix_ri_ingredient", "ingredient_id"),
    )


# ─── Food Nutrients (영양 DB: 100g 기준) ─────────────
class FoodNutrient(Base):
    __tablename__ = "food_nutrients"

    id = Column(Integer, primary_key=True, index=True)
    food_name = Column(String(200), nullable=False, index=True)
    source_code = Column(String(50), nullable=True, index=True)  # 공공DB 식품코드
    kcal_per_100g = Column(Float, default=0)
    carb_g_per_100g = Column(Float, default=0)
    protein_g_per_100g = Column(Float, default=0)
    fat_g_per_100g = Column(Float, default=0)
    sodium_mg_per_100g = Column(Float, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow)


# ─── Ingredient ↔ Nutrient 매칭 ─────────────────────
class IngredientNutrientMap(Base):
    __tablename__ = "ingredient_nutrient_map"

    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), primary_key=True)
    food_nutrient_id = Column(Integer, ForeignKey("food_nutrients.id"), nullable=False)
    match_confidence = Column(Float, default=1.0)  # 0~1
    match_method = Column(SQLEnum(MatchMethod), default=MatchMethod.MANUAL)
    updated_at = Column(DateTime, default=datetime.utcnow)

    ingredient = relationship("Ingredient", back_populates="nutrient_map")
    food_nutrient = relationship("FoodNutrient")


# ─── Menu Plans (주간식단) ───────────────────────────
class MenuPlan(Base):
    __tablename__ = "menu_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    week_start = Column(Date, nullable=False)     # 월요일 기준
    rotation_key = Column(String(1), default="A")  # A/B
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="menu_plans")
    items = relationship("MenuPlanItem", back_populates="menu_plan", cascade="all, delete-orphan")
    shopping_list = relationship("ShoppingList", back_populates="menu_plan", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("user_id", "week_start", name="uq_user_week"),
    )


class MenuPlanItem(Base):
    __tablename__ = "menu_plan_items"

    id = Column(Integer, primary_key=True, index=True)
    menu_plan_id = Column(Integer, ForeignKey("menu_plans.id"), nullable=False)
    date = Column(Date, nullable=False)
    meal_type = Column(SQLEnum(MealType), nullable=False)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    servings_for_user = Column(Float, default=1.0)
    kcal_est = Column(Float, nullable=True)
    macros_est = Column(JSON, nullable=True)  # {"carb":..., "protein":..., "fat":..., "sodium":...}

    menu_plan = relationship("MenuPlan", back_populates="items")
    recipe = relationship("Recipe")


# ─── Shopping Lists (장보기) ─────────────────────────
class ShoppingList(Base):
    __tablename__ = "shopping_lists"

    id = Column(Integer, primary_key=True, index=True)
    menu_plan_id = Column(Integer, ForeignKey("menu_plans.id"), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    menu_plan = relationship("MenuPlan", back_populates="shopping_list")
    items = relationship("ShoppingListItem", back_populates="shopping_list", cascade="all, delete-orphan")


class ShoppingListItem(Base):
    __tablename__ = "shopping_list_items"

    id = Column(Integer, primary_key=True, index=True)
    shopping_list_id = Column(Integer, ForeignKey("shopping_lists.id"), nullable=False)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), nullable=False)
    total_qty = Column(Float, nullable=False)
    unit = Column(String(20), default="g")
    is_pantry = Column(Boolean, default=False)   # 상비 재료
    checked = Column(Boolean, default=False)      # 구매 완료
    note = Column(String(200), nullable=True)

    shopping_list = relationship("ShoppingList", back_populates="items")
    ingredient = relationship("Ingredient")
