import 'package:flutter/material.dart';
import '../models/models.dart';
import '../services/api_service.dart';

class AppState extends ChangeNotifier {
  final ApiService api = ApiService();

  // 인증 상태
  bool isLoggedIn = false;
  Map<String, dynamic>? userInfo;

  // 사용자
  UserModel? currentUser;
  int get userId => api.userId ?? currentUser?.id ?? 1;

  // 오늘 메뉴
  TodayMenuModel? todayMenu;
  bool todayLoading = false;

  // 주간 메뉴
  MenuPlanModel? weeklyMenu;
  bool weeklyLoading = false;

  // 장보기
  List<ShoppingItemModel> shoppingItems = [];
  bool shoppingLoading = false;

  // 에러 메시지
  String? errorMessage;

  // ─── 인증 ─────────────────────
  void onLoginSuccess(Map<String, dynamic> result) {
    isLoggedIn = true;
    userInfo = result['user'];
    final u = result['user'];
    currentUser = UserModel(
      id: u['id'],
      name: u['name'],
      birthYear: u['birth_year'],
      sex: u['sex'],
      heightCm: u['height_cm']?.toDouble(),
      weightKg: u['weight_kg']?.toDouble(),
      activityLevel: u['activity_level'] ?? 2,
      kcalTarget: u['kcal_target'],
    );
    notifyListeners();
  }

  void logout() {
    api.logout();
    isLoggedIn = false;
    currentUser = null;
    userInfo = null;
    todayMenu = null;
    weeklyMenu = null;
    shoppingItems = [];
    notifyListeners();
  }

  // ─── 초기화 (비로그인 모드 호환) ───
  Future<void> initialize() async {
    if (isLoggedIn) return;
    try {
      currentUser = await api.getUser(1);
    } catch (_) {
      try {
        currentUser = await api.createUser({
          'name': '사용자',
          'birth_year': 1960,
          'sex': 'F',
          'height_cm': 158,
          'weight_kg': 60,
          'activity_level': 2,
        });
      } catch (e) {
        errorMessage = '서버 연결에 실패했습니다';
      }
    }
    notifyListeners();
  }

  // ─── 오늘 메뉴 ────────────────
  Future<void> loadTodayMenu() async {
    todayLoading = true;
    errorMessage = null;
    notifyListeners();

    try {
      todayMenu = await api.getTodayMenu(userId);
    } catch (e) {
      try {
        final now = DateTime.now();
        final monday = now.subtract(Duration(days: now.weekday - 1));
        final weekStart =
            '${monday.year}-${monday.month.toString().padLeft(2, '0')}-${monday.day.toString().padLeft(2, '0')}';

        await api.generateMenu(userId, weekStart);
        todayMenu = await api.getTodayMenu(userId);
      } catch (e2) {
        errorMessage = '메뉴를 불러올 수 없습니다';
      }
    }

    todayLoading = false;
    notifyListeners();
  }

  // ─── 주간 메뉴 ────────────────
  Future<void> loadWeeklyMenu() async {
    weeklyLoading = true;
    notifyListeners();

    try {
      weeklyMenu = await api.getCurrentMenu(userId);
    } catch (e) {
      try {
        final now = DateTime.now();
        final monday = now.subtract(Duration(days: now.weekday - 1));
        final weekStart =
            '${monday.year}-${monday.month.toString().padLeft(2, '0')}-${monday.day.toString().padLeft(2, '0')}';

        weeklyMenu = await api.generateMenu(userId, weekStart);
      } catch (_) {
        errorMessage = '주간 메뉴를 불러올 수 없습니다';
      }
    }

    weeklyLoading = false;
    notifyListeners();
  }

  // ─── 한 끼 교체 ───────────────
  Future<void> replaceMeal(int itemId) async {
    try {
      await api.replaceMealItem(itemId);
      await loadTodayMenu();
      await loadWeeklyMenu();
    } catch (e) {
      errorMessage = '메뉴 교체에 실패했습니다';
      notifyListeners();
    }
  }

  // ─── 장보기 ───────────────────
  Future<void> loadShopping() async {
    shoppingLoading = true;
    notifyListeners();

    try {
      shoppingItems = await api.getCurrentShopping(userId);
    } catch (e) {
      shoppingItems = [];
    }

    shoppingLoading = false;
    notifyListeners();
  }

  Future<void> toggleShoppingItem(int itemId, bool checked) async {
    final idx = shoppingItems.indexWhere((i) => i.id == itemId);
    if (idx >= 0) {
      shoppingItems[idx].checked = checked;
      notifyListeners();
    }

    try {
      await api.checkShoppingItem(itemId, checked);
    } catch (_) {}
  }
}
