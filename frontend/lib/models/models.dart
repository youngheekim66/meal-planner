/// API 응답 데이터 모델

class UserModel {
  final int id;
  final String name;
  final int? birthYear;
  final String? sex;
  final double? heightCm;
  final double? weightKg;
  final int activityLevel;
  final int? kcalTarget;

  UserModel({
    required this.id,
    required this.name,
    this.birthYear,
    this.sex,
    this.heightCm,
    this.weightKg,
    this.activityLevel = 2,
    this.kcalTarget,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'],
      name: json['name'],
      birthYear: json['birth_year'],
      sex: json['sex'],
      heightCm: json['height_cm']?.toDouble(),
      weightKg: json['weight_kg']?.toDouble(),
      activityLevel: json['activity_level'] ?? 2,
      kcalTarget: json['kcal_target'],
    );
  }
}

class RecipeModel {
  final int id;
  final String title;
  final String cuisine;
  final List<String> tags;
  final List<String> mealTypes;
  final int difficulty;
  final int cookTimeMin;
  final int servings;
  final List<Map<String, dynamic>> steps;
  final String? sourceUrl;
  final String? thumbnailUrl;
  final double? kcalPerServing;
  final Map<String, dynamic>? macrosPerServing;

  RecipeModel({
    required this.id,
    required this.title,
    required this.cuisine,
    required this.tags,
    required this.mealTypes,
    required this.difficulty,
    required this.cookTimeMin,
    required this.servings,
    required this.steps,
    this.sourceUrl,
    this.thumbnailUrl,
    this.kcalPerServing,
    this.macrosPerServing,
  });

  factory RecipeModel.fromJson(Map<String, dynamic> json) {
    return RecipeModel(
      id: json['id'],
      title: json['title'] ?? '',
      cuisine: json['cuisine'] ?? 'KOREAN',
      tags: List<String>.from(json['tags'] ?? []),
      mealTypes: List<String>.from(json['meal_types'] ?? []),
      difficulty: json['difficulty'] ?? 2,
      cookTimeMin: json['cook_time_min'] ?? 30,
      servings: json['servings'] ?? 2,
      steps: List<Map<String, dynamic>>.from(json['steps'] ?? []),
      sourceUrl: json['source_url'],
      thumbnailUrl: json['thumbnail_url'],
      kcalPerServing: json['kcal_per_serving']?.toDouble(),
      macrosPerServing: json['macros_per_serving'],
    );
  }

  String get difficultyText {
    switch (difficulty) {
      case 1: return '쉬움';
      case 2: return '보통';
      case 3: return '어려움';
      default: return '보통';
    }
  }

  String get difficultyDots {
    return '●' * difficulty + '○' * (3 - difficulty);
  }
}

class MenuPlanItemModel {
  final int id;
  final String date;
  final String mealType;
  final RecipeModel recipe;
  final double servingsForUser;
  final double? kcalEst;

  MenuPlanItemModel({
    required this.id,
    required this.date,
    required this.mealType,
    required this.recipe,
    required this.servingsForUser,
    this.kcalEst,
  });

  factory MenuPlanItemModel.fromJson(Map<String, dynamic> json) {
    return MenuPlanItemModel(
      id: json['id'],
      date: json['date'],
      mealType: json['meal_type'],
      recipe: RecipeModel.fromJson(json['recipe']),
      servingsForUser: (json['servings_for_user'] ?? 1.0).toDouble(),
      kcalEst: json['kcal_est']?.toDouble(),
    );
  }

  String get mealTypeKorean {
    switch (mealType) {
      case 'BREAKFAST': return '아침';
      case 'LUNCH': return '점심';
      case 'DINNER': return '저녁';
      default: return mealType;
    }
  }
}

class MenuPlanModel {
  final int id;
  final String weekStart;
  final String rotationKey;
  final List<MenuPlanItemModel> items;
  final double? totalKcal;
  final List<Map<String, dynamic>>? dailySummary;

  MenuPlanModel({
    required this.id,
    required this.weekStart,
    required this.rotationKey,
    required this.items,
    this.totalKcal,
    this.dailySummary,
  });

  factory MenuPlanModel.fromJson(Map<String, dynamic> json) {
    return MenuPlanModel(
      id: json['id'],
      weekStart: json['week_start'],
      rotationKey: json['rotation_key'] ?? 'A',
      items: (json['items'] as List)
          .map((e) => MenuPlanItemModel.fromJson(e))
          .toList(),
      totalKcal: json['total_kcal']?.toDouble(),
      dailySummary: json['daily_summary'] != null
          ? List<Map<String, dynamic>>.from(json['daily_summary'])
          : null,
    );
  }

  List<MenuPlanItemModel> getItemsForDate(String dateStr) {
    return items.where((i) => i.date == dateStr).toList();
  }
}

class ShoppingItemModel {
  final int id;
  final String ingredientName;
  final String category;
  final double totalQty;
  final String unit;
  final bool isPantry;
  bool checked;

  ShoppingItemModel({
    required this.id,
    required this.ingredientName,
    required this.category,
    required this.totalQty,
    required this.unit,
    required this.isPantry,
    this.checked = false,
  });

  factory ShoppingItemModel.fromJson(Map<String, dynamic> json) {
    final ing = json['ingredient'] ?? {};
    return ShoppingItemModel(
      id: json['id'],
      ingredientName: ing['name_std'] ?? '알 수 없음',
      category: ing['category'] ?? '기타',
      totalQty: (json['total_qty'] ?? 0).toDouble(),
      unit: json['unit'] ?? 'g',
      isPantry: json['is_pantry'] ?? false,
      checked: json['checked'] ?? false,
    );
  }

  String get displayQty {
    if (totalQty == totalQty.roundToDouble()) {
      return '${totalQty.toInt()} $unit';
    }
    return '${totalQty.toStringAsFixed(1)} $unit';
  }
}

class TodayMenuModel {
  final String date;
  final Map<String, dynamic> meals;
  final double totalKcal;

  TodayMenuModel({
    required this.date,
    required this.meals,
    required this.totalKcal,
  });

  factory TodayMenuModel.fromJson(Map<String, dynamic> json) {
    return TodayMenuModel(
      date: json['date'] ?? '',
      meals: Map<String, dynamic>.from(json['meals'] ?? {}),
      totalKcal: (json['total_kcal'] ?? 0).toDouble(),
    );
  }
}
