import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../services/app_state.dart';
import '../theme/app_theme.dart';
import 'recipe_detail_screen.dart';

class TodayScreen extends StatefulWidget {
  const TodayScreen({super.key});

  @override
  State<TodayScreen> createState() => _TodayScreenState();
}

class _TodayScreenState extends State<TodayScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<AppState>().loadTodayMenu();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<AppState>(
      builder: (context, state, _) {
        if (state.todayLoading) {
          return const Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                CircularProgressIndicator(),
                SizedBox(height: 16),
                Text('오늘 식단을 준비하고 있어요...', style: TextStyle(fontSize: 18)),
              ],
            ),
          );
        }

        if (state.errorMessage != null && state.todayMenu == null) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.cloud_off, size: 64, color: Colors.grey),
                const SizedBox(height: 16),
                Text(state.errorMessage!, style: const TextStyle(fontSize: 18)),
                const SizedBox(height: 24),
                ElevatedButton.icon(
                  onPressed: () => state.loadTodayMenu(),
                  icon: const Icon(Icons.refresh),
                  label: const Text('다시 시도'),
                ),
              ],
            ),
          );
        }

        final today = state.todayMenu;
        if (today == null) {
          return const Center(child: Text('식단 정보가 없습니다', style: TextStyle(fontSize: 18)));
        }

        return RefreshIndicator(
          onRefresh: () => state.loadTodayMenu(),
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              // 날짜 헤더
              _buildDateHeader(today.date),
              const SizedBox(height: 8),

              // 일일 칼로리 요약
              _buildKcalSummary(today.totalKcal, state.currentUser?.kcalTarget),
              const SizedBox(height: 16),

              // 끼니별 카드
              for (final mealType in ['BREAKFAST', 'LUNCH', 'DINNER'])
                if (today.meals.containsKey(mealType))
                  _buildMealCard(context, state, mealType, today.meals[mealType]),
            ],
          ),
        );
      },
    );
  }

  Widget _buildDateHeader(String dateStr) {
    final date = DateTime.tryParse(dateStr) ?? DateTime.now();
    final weekdays = ['월', '화', '수', '목', '금', '토', '일'];
    final formatted = '${date.month}월 ${date.day}일 (${weekdays[date.weekday - 1]})';

    return Container(
      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
      decoration: BoxDecoration(
        color: AppTheme.primary.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          const Icon(Icons.calendar_today, color: AppTheme.primary, size: 28),
          const SizedBox(width: 12),
          Text(
            '오늘  $formatted',
            style: const TextStyle(
              fontSize: AppTheme.fontHeading,
              fontWeight: FontWeight.bold,
              color: AppTheme.primaryDark,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildKcalSummary(double totalKcal, int? target) {
    final ratio = target != null && target > 0 ? totalKcal / target : 0.0;
    final color = ratio > 1.1 ? AppTheme.kcalOver : ratio > 0.9 ? AppTheme.kcalWarn : AppTheme.kcalGood;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Icon(Icons.local_fire_department, color: color, size: 32),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '오늘 예상 ${totalKcal.toInt()} kcal',
                    style: TextStyle(fontSize: AppTheme.fontBody, fontWeight: FontWeight.bold, color: color),
                  ),
                  if (target != null)
                    Text(
                      '권장 $target kcal',
                      style: const TextStyle(fontSize: AppTheme.fontCaption, color: AppTheme.textSecondary),
                    ),
                ],
              ),
            ),
            if (target != null)
              SizedBox(
                width: 60, height: 60,
                child: Stack(
                  alignment: Alignment.center,
                  children: [
                    CircularProgressIndicator(
                      value: ratio.clamp(0.0, 1.5),
                      strokeWidth: 6,
                      backgroundColor: Colors.grey[200],
                      color: color,
                    ),
                    Text('${(ratio * 100).toInt()}%',
                      style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: color)),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildMealCard(BuildContext context, AppState state, String mealType, Map<String, dynamic> meal) {
    final mealNames = {'BREAKFAST': '🌅 아침', 'LUNCH': '☀️ 점심', 'DINNER': '🌙 저녁'};
    final title = meal['title'] ?? '미정';
    final kcal = meal['kcal'];
    final cookTime = meal['cook_time_min'] ?? 0;
    final difficulty = meal['difficulty'] ?? 2;
    final itemId = meal['item_id'];
    final recipeId = meal['recipe_id'];

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: recipeId != null
            ? () => Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => RecipeDetailScreen(recipeId: recipeId)),
              )
            : null,
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 끼니 라벨
              Text(
                mealNames[mealType] ?? mealType,
                style: const TextStyle(fontSize: AppTheme.fontCaption, color: AppTheme.textSecondary),
              ),
              const SizedBox(height: 8),

              // 메뉴 이름
              Text(
                title,
                style: const TextStyle(fontSize: AppTheme.fontHeading, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),

              // 정보 행
              Row(
                children: [
                  if (kcal != null) ...[
                    Icon(Icons.local_fire_department, size: 20, color: AppTheme.accent),
                    const SizedBox(width: 4),
                    Text('${(kcal as num).toInt()} kcal', style: const TextStyle(fontSize: AppTheme.fontCaption)),
                    const SizedBox(width: 16),
                  ],
                  const Icon(Icons.timer_outlined, size: 20, color: AppTheme.textSecondary),
                  const SizedBox(width: 4),
                  Text('$cookTime분', style: const TextStyle(fontSize: AppTheme.fontCaption)),
                  const SizedBox(width: 16),
                  Text('난이도 ${'●' * difficulty}${'○' * (3 - difficulty)}',
                    style: const TextStyle(fontSize: AppTheme.fontCaption)),
                ],
              ),
              const SizedBox(height: 16),

              // 버튼들
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: recipeId != null
                          ? () => Navigator.push(
                              context,
                              MaterialPageRoute(builder: (_) => RecipeDetailScreen(recipeId: recipeId)),
                            )
                          : null,
                      icon: const Icon(Icons.restaurant_menu, size: 20),
                      label: const Text('조리순서'),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: itemId != null ? () => _showReplaceDialog(context, state, itemId, title) : null,
                      icon: const Icon(Icons.swap_horiz, size: 20),
                      label: const Text('메뉴 변경'),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showReplaceDialog(BuildContext context, AppState state, int itemId, String currentTitle) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('메뉴 변경', style: TextStyle(fontSize: AppTheme.fontHeading)),
        content: Text(
          '"$currentTitle"을(를)\n다른 메뉴로 바꿀까요?',
          style: const TextStyle(fontSize: AppTheme.fontBody),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('취소', style: TextStyle(fontSize: AppTheme.fontCaption)),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(ctx);
              state.replaceMeal(itemId);
            },
            child: const Text('변경하기'),
          ),
        ],
      ),
    );
  }
}
