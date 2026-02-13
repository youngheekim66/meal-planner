import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/app_state.dart';
import '../models/models.dart';
import '../theme/app_theme.dart';
import 'recipe_detail_screen.dart';

class WeeklyScreen extends StatefulWidget {
  const WeeklyScreen({super.key});

  @override
  State<WeeklyScreen> createState() => _WeeklyScreenState();
}

class _WeeklyScreenState extends State<WeeklyScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<AppState>().loadWeeklyMenu();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<AppState>(
      builder: (context, state, _) {
        if (state.weeklyLoading) {
          return const Center(child: CircularProgressIndicator());
        }

        final menu = state.weeklyMenu;
        if (menu == null) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Text('주간 메뉴가 없습니다', style: TextStyle(fontSize: 18)),
                const SizedBox(height: 16),
                ElevatedButton.icon(
                  onPressed: () => state.loadWeeklyMenu(),
                  icon: const Icon(Icons.add),
                  label: const Text('메뉴 생성하기'),
                ),
              ],
            ),
          );
        }

        return RefreshIndicator(
          onRefresh: () => state.loadWeeklyMenu(),
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              // 헤더
              _buildHeader(menu),
              const SizedBox(height: 12),

              // 요일별 카드
              ..._buildDayCards(context, state, menu),
            ],
          ),
        );
      },
    );
  }

  Widget _buildHeader(MenuPlanModel menu) {
    return Card(
      color: AppTheme.primary.withOpacity(0.1),
      elevation: 0,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            const Icon(Icons.date_range, color: AppTheme.primary, size: 28),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '${menu.weekStart} 주간 메뉴',
                    style: const TextStyle(fontSize: AppTheme.fontBody, fontWeight: FontWeight.bold),
                  ),
                  Text(
                    '로테이션 ${menu.rotationKey} | 총 ${menu.totalKcal?.toInt() ?? 0} kcal',
                    style: const TextStyle(fontSize: AppTheme.fontCaption, color: AppTheme.textSecondary),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  List<Widget> _buildDayCards(BuildContext context, AppState state, MenuPlanModel menu) {
    final weekdays = ['월', '화', '수', '목', '금', '토', '일'];
    final List<Widget> cards = [];

    // 날짜별로 그룹화
    final dateSet = menu.items.map((i) => i.date).toSet().toList()..sort();

    for (int i = 0; i < dateSet.length; i++) {
      final dateStr = dateSet[i];
      final dayItems = menu.getItemsForDate(dateStr);
      final date = DateTime.tryParse(dateStr);
      final dayLabel = date != null ? weekdays[date.weekday - 1] : '';
      final isToday = dateStr == DateTime.now().toString().substring(0, 10);
      final isWeekend = date != null && (date.weekday == 6 || date.weekday == 7);

      // 일별 칼로리 합산
      double dayKcal = 0;
      for (final item in dayItems) {
        dayKcal += item.kcalEst ?? 0;
      }

      cards.add(
        Card(
          margin: const EdgeInsets.only(bottom: 8),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: isToday
                ? const BorderSide(color: AppTheme.primary, width: 2)
                : BorderSide.none,
          ),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // 요일 헤더
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: isToday
                            ? AppTheme.primary
                            : isWeekend
                                ? AppTheme.accent.withOpacity(0.2)
                                : Colors.grey[200],
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        '$dayLabel요일',
                        style: TextStyle(
                          fontSize: AppTheme.fontCaption,
                          fontWeight: FontWeight.bold,
                          color: isToday ? Colors.white : AppTheme.textPrimary,
                        ),
                      ),
                    ),
                    if (isToday) ...[
                      const SizedBox(width: 8),
                      const Text('오늘', style: TextStyle(
                        fontSize: AppTheme.fontCaption, color: AppTheme.primary, fontWeight: FontWeight.bold)),
                    ],
                    const Spacer(),
                    Text(
                      '${dayKcal.toInt()} kcal',
                      style: const TextStyle(fontSize: AppTheme.fontSmall, color: AppTheme.textSecondary),
                    ),
                  ],
                ),
                const Divider(height: 20),

                // 끼니별
                for (final item in dayItems) _buildMealRow(context, state, item),
              ],
            ),
          ),
        ),
      );
    }

    return cards;
  }

  Widget _buildMealRow(BuildContext context, AppState state, MenuPlanItemModel item) {
    final mealIcons = {'BREAKFAST': '🌅', 'LUNCH': '☀️', 'DINNER': '🌙'};

    return InkWell(
      onTap: () => Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => RecipeDetailScreen(recipeId: item.recipe.id)),
      ),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 6),
        child: Row(
          children: [
            Text(
              mealIcons[item.mealType] ?? '🍽️',
              style: const TextStyle(fontSize: 20),
            ),
            const SizedBox(width: 8),
            Text(
              item.mealTypeKorean,
              style: const TextStyle(fontSize: AppTheme.fontCaption, color: AppTheme.textSecondary),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                item.recipe.title,
                style: const TextStyle(fontSize: AppTheme.fontCaption, fontWeight: FontWeight.w500),
                overflow: TextOverflow.ellipsis,
              ),
            ),
            if (item.kcalEst != null)
              Text(
                '${item.kcalEst!.toInt()} kcal',
                style: const TextStyle(fontSize: AppTheme.fontSmall, color: AppTheme.textSecondary),
              ),
            const SizedBox(width: 8),
            // 교체 버튼
            GestureDetector(
              onTap: () => state.replaceMeal(item.id),
              child: const Icon(Icons.swap_horiz, size: 22, color: AppTheme.textSecondary),
            ),
          ],
        ),
      ),
    );
  }
}
