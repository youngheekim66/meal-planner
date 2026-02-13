import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'theme/app_theme.dart';
import 'services/app_state.dart';
import 'screens/auth_screen.dart';
import 'screens/today_screen.dart';
import 'screens/weekly_screen.dart';
import 'screens/shopping_screen.dart';

void main() {
  runApp(
    ChangeNotifierProvider(
      create: (_) => AppState(),
      child: const MealPlannerApp(),
    ),
  );
}

class MealPlannerApp extends StatelessWidget {
  const MealPlannerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '식단 플래너',
      theme: AppTheme.theme,
      debugShowCheckedModeBanner: false,
      home: const AuthGate(),
    );
  }
}

/// 인증 게이트: 로그인 전 → AuthScreen, 로그인 후 → HomeShell
class AuthGate extends StatelessWidget {
  const AuthGate({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<AppState>(
      builder: (_, state, __) {
        if (state.isLoggedIn) {
          return const HomeShell();
        }
        return AuthScreen(
          api: state.api,
          onLoginSuccess: (result) => state.onLoginSuccess(result),
        );
      },
    );
  }
}

/// 하단 탭 3개: 오늘 / 주간 / 장보기
class HomeShell extends StatefulWidget {
  const HomeShell({super.key});

  @override
  State<HomeShell> createState() => _HomeShellState();
}

class _HomeShellState extends State<HomeShell> {
  int _currentIndex = 0;

  final List<Widget> _screens = const [
    TodayScreen(),
    WeeklyScreen(),
    ShoppingScreen(),
  ];

  final List<String> _titles = ['오늘 식단', '주간 메뉴', '장보기'];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_titles[_currentIndex]),
        actions: [
          if (_currentIndex == 0)
            IconButton(
              icon: const Icon(Icons.settings, size: 28),
              onPressed: () => _showSettingsDialog(context),
              tooltip: '설정',
            ),
        ],
      ),
      body: _screens[_currentIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) => setState(() => _currentIndex = index),
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.restaurant, size: 28),
            label: '오늘',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.calendar_month, size: 28),
            label: '주간',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.shopping_cart, size: 28),
            label: '장보기',
          ),
        ],
      ),
    );
  }

  void _showSettingsDialog(BuildContext context) {
    final state = context.read<AppState>();
    final user = state.currentUser;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('⚙️ 설정',
                style: TextStyle(
                    fontSize: AppTheme.fontTitle,
                    fontWeight: FontWeight.bold)),
            const SizedBox(height: 24),

            if (user != null) ...[
              _settingRow('이름', user.name),
              _settingRow('성별', user.sex == 'M' ? '남성' : '여성'),
              _settingRow('출생연도', '${user.birthYear ?? "-"}년'),
              _settingRow('키 / 몸무게',
                  '${user.heightCm?.toInt() ?? "-"}cm / ${user.weightKg?.toInt() ?? "-"}kg'),
              _settingRow('활동량', '${user.activityLevel} / 5'),
              if (user.kcalTarget != null)
                _settingRow('일일 권장 칼로리', '${user.kcalTarget} kcal'),
              const Divider(height: 32),
            ],

            // 메뉴 재생성
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: () {
                  Navigator.pop(ctx);
                  state.loadWeeklyMenu();
                  state.loadTodayMenu();
                  state.loadShopping();
                },
                icon: const Icon(Icons.refresh),
                label: const Text('이번 주 메뉴 새로 만들기'),
              ),
            ),
            const SizedBox(height: 12),

            // 로그아웃
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: () {
                  Navigator.pop(ctx);
                  state.logout();
                },
                icon: const Icon(Icons.logout, color: Colors.red),
                label: const Text('로그아웃', style: TextStyle(color: Colors.red)),
                style: OutlinedButton.styleFrom(
                  side: const BorderSide(color: Colors.red),
                ),
              ),
            ),
            const SizedBox(height: 16),

            // 앱 정보
            const Center(
              child: Text(
                '식단 플래너 v1.2\n50~70대를 위한 건강한 식단 관리',
                style: TextStyle(
                    fontSize: AppTheme.fontSmall,
                    color: AppTheme.textSecondary),
                textAlign: TextAlign.center,
              ),
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }

  Widget _settingRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          SizedBox(
            width: 120,
            child: Text(label,
                style: const TextStyle(
                    fontSize: AppTheme.fontCaption,
                    color: AppTheme.textSecondary)),
          ),
          Expanded(
            child: Text(value,
                style: const TextStyle(
                    fontSize: AppTheme.fontBody,
                    fontWeight: FontWeight.w500)),
          ),
        ],
      ),
    );
  }
}
