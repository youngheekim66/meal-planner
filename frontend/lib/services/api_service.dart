import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/models.dart';

class ApiService {
  // 개발 환경: Android 에뮬레이터 → 10.0.2.2, iOS 시뮬레이터 → localhost
  // 실제 기기 → PC의 로컬 IP (예: 192.168.0.10)
static const String baseUrl = 'https://meal-planner-production-81ed.up.railway.app';

  // JWT 토큰 (로그인 후 저장)
  String? _token;
  int? _userId;

  String? get token => _token;
  int? get userId => _userId;
  bool get isLoggedIn => _token != null;

  Map<String, String> get _authHeaders => {
    'Content-Type': 'application/json',
    if (_token != null) 'Authorization': 'Bearer $_token',
  };

  // ─── Auth (인증) ─────────────────────────
  Future<Map<String, dynamic>> signup({
    required String email,
    required String password,
    required String name,
    int? birthYear,
    String? sex,
    double? heightCm,
    double? weightKg,
    int activityLevel = 2,
  }) async {
    final res = await http.post(
      Uri.parse('$baseUrl/auth/signup'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'email': email,
        'password': password,
        'name': name,
        if (birthYear != null) 'birth_year': birthYear,
        if (sex != null) 'sex': sex,
        if (heightCm != null) 'height_cm': heightCm,
        if (weightKg != null) 'weight_kg': weightKg,
        'activity_level': activityLevel,
      }),
    );
    if (res.statusCode == 201) {
      final data = jsonDecode(res.body);
      _token = data['access_token'];
      _userId = data['user']['id'];
      return data;
    }
    final err = jsonDecode(res.body);
    throw Exception(err['detail'] ?? '회원가입 실패');
  }

  Future<Map<String, dynamic>> login({
    required String email,
    required String password,
  }) async {
    final res = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}),
    );
    if (res.statusCode == 200) {
      final data = jsonDecode(res.body);
      _token = data['access_token'];
      _userId = data['user']['id'];
      return data;
    }
    final err = jsonDecode(res.body);
    throw Exception(err['detail'] ?? '로그인 실패');
  }

  Future<Map<String, dynamic>> getMe() async {
    final res = await http.get(
      Uri.parse('$baseUrl/auth/me'),
      headers: _authHeaders,
    );
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    }
    throw Exception('내 정보 조회 실패');
  }

  void logout() {
    _token = null;
    _userId = null;
  }

  // ─── Users ────────────────────────────────
  Future<UserModel> createUser(Map<String, dynamic> data) async {
    final res = await http.post(
      Uri.parse('$baseUrl/users/'),
      headers: _authHeaders,
      body: jsonEncode(data),
    );
    if (res.statusCode == 200) {
      return UserModel.fromJson(jsonDecode(res.body));
    }
    throw Exception('사용자 등록 실패: ${res.body}');
  }

  Future<UserModel> getUser(int userId) async {
    final res = await http.get(
      Uri.parse('$baseUrl/users/$userId'),
      headers: _authHeaders,
    );
    if (res.statusCode == 200) {
      return UserModel.fromJson(jsonDecode(res.body));
    }
    throw Exception('사용자 조회 실패');
  }

  // ─── TDEE ─────────────────────────────────
  Future<Map<String, dynamic>> calculateTDEE(Map<String, dynamic> data) async {
    final res = await http.post(
      Uri.parse('$baseUrl/users/tdee'),
      headers: _authHeaders,
      body: jsonEncode(data),
    );
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    }
    throw Exception('TDEE 계산 실패');
  }

  // ─── Recipes ──────────────────────────────
  Future<List<RecipeModel>> getRecipes({String? cuisine, int limit = 50}) async {
    var url = '$baseUrl/recipes/?limit=$limit';
    if (cuisine != null) url += '&cuisine=$cuisine';

    final res = await http.get(Uri.parse(url), headers: _authHeaders);
    if (res.statusCode == 200) {
      final List<dynamic> data = jsonDecode(res.body);
      return data.map((e) => RecipeModel.fromJson(e)).toList();
    }
    throw Exception('레시피 목록 조회 실패');
  }

  Future<RecipeModel> getRecipe(int recipeId) async {
    final res = await http.get(
      Uri.parse('$baseUrl/recipes/$recipeId'),
      headers: _authHeaders,
    );
    if (res.statusCode == 200) {
      return RecipeModel.fromJson(jsonDecode(res.body));
    }
    throw Exception('레시피 조회 실패');
  }

  Future<List<dynamic>> getRecipeIngredients(int recipeId) async {
    final res = await http.get(
      Uri.parse('$baseUrl/recipes/$recipeId/ingredients'),
      headers: _authHeaders,
    );
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    }
    throw Exception('재료 조회 실패');
  }

  // ─── Nutrition ────────────────────────────
  Future<Map<String, dynamic>> getRecipeNutrition(int recipeId) async {
    final res = await http.get(
      Uri.parse('$baseUrl/recipes/$recipeId/nutrition'),
      headers: _authHeaders,
    );
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    }
    throw Exception('영양정보 조회 실패');
  }

  // ─── Menu Plans ───────────────────────────
  Future<MenuPlanModel> generateMenu(int userId, String weekStart) async {
    final res = await http.post(
      Uri.parse('$baseUrl/menu/generate'),
      headers: _authHeaders,
      body: jsonEncode({'user_id': userId, 'week_start': weekStart}),
    );
    if (res.statusCode == 200) {
      return MenuPlanModel.fromJson(jsonDecode(res.body));
    }
    throw Exception('메뉴 생성 실패: ${res.body}');
  }

  Future<MenuPlanModel> getCurrentMenu(int userId) async {
    final res = await http.get(
      Uri.parse('$baseUrl/menu/$userId/current'),
      headers: _authHeaders,
    );
    if (res.statusCode == 200) {
      return MenuPlanModel.fromJson(jsonDecode(res.body));
    }
    throw Exception('주간 메뉴 조회 실패');
  }

  Future<TodayMenuModel> getTodayMenu(int userId) async {
    final res = await http.get(
      Uri.parse('$baseUrl/menu/$userId/today'),
      headers: _authHeaders,
    );
    if (res.statusCode == 200) {
      return TodayMenuModel.fromJson(jsonDecode(res.body));
    }
    throw Exception('오늘 메뉴 조회 실패');
  }

  Future<Map<String, dynamic>> replaceMealItem(int itemId) async {
    final res = await http.post(
      Uri.parse('$baseUrl/menu/item/$itemId/replace'),
      headers: _authHeaders,
    );
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    }
    throw Exception('메뉴 교체 실패');
  }

  // ─── Shopping Lists ───────────────────────
  Future<List<ShoppingItemModel>> getCurrentShopping(int userId) async {
    final res = await http.get(
      Uri.parse('$baseUrl/shopping/$userId/current'),
      headers: _authHeaders,
    );
    if (res.statusCode == 200) {
      final data = jsonDecode(res.body);
      final items = data['items'] as List;
      return items.map((e) => ShoppingItemModel.fromJson(e)).toList();
    }
    throw Exception('장보기 리스트 조회 실패');
  }

  Future<void> checkShoppingItem(int itemId, bool checked) async {
    await http.patch(
      Uri.parse('$baseUrl/shopping/item/check'),
      headers: _authHeaders,
      body: jsonEncode({'item_id': itemId, 'checked': checked}),
    );
  }
}
