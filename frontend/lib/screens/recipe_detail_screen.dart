import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/models.dart';
import '../theme/app_theme.dart';

class RecipeDetailScreen extends StatefulWidget {
  final int recipeId;
  const RecipeDetailScreen({super.key, required this.recipeId});

  @override
  State<RecipeDetailScreen> createState() => _RecipeDetailScreenState();
}

class _RecipeDetailScreenState extends State<RecipeDetailScreen> with SingleTickerProviderStateMixin {
  final ApiService _api = ApiService();
  late TabController _tabController;

  RecipeModel? recipe;
  List<dynamic>? ingredients;
  bool loading = true;
  int _currentStep = 0;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      final r = await _api.getRecipe(widget.recipeId);
      final ing = await _api.getRecipeIngredients(widget.recipeId);
      setState(() {
        recipe = r;
        ingredients = ing;
        loading = false;
      });
    } catch (e) {
      setState(() => loading = false);
    }
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (loading) {
      return Scaffold(
        appBar: AppBar(title: const Text('레시피')),
        body: const Center(child: CircularProgressIndicator()),
      );
    }

    if (recipe == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('레시피')),
        body: const Center(child: Text('레시피를 불러올 수 없습니다', style: TextStyle(fontSize: 18))),
      );
    }

    return Scaffold(
      appBar: AppBar(title: Text(recipe!.title)),
      body: Column(
        children: [
          // 핵심 요약
          _buildSummaryHeader(),

          // 탭
          TabBar(
            controller: _tabController,
            labelStyle: const TextStyle(fontSize: AppTheme.fontCaption, fontWeight: FontWeight.bold),
            tabs: const [
              Tab(text: '조리순서'),
              Tab(text: '재료'),
              Tab(text: '영양정보'),
            ],
          ),

          // 탭 내용
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                _buildStepsTab(),
                _buildIngredientsTab(),
                _buildNutritionTab(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryHeader() {
    return Container(
      padding: const EdgeInsets.all(20),
      color: AppTheme.primary.withOpacity(0.05),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _infoChip(Icons.local_fire_department, AppTheme.accent,
              recipe!.kcalPerServing != null ? '${recipe!.kcalPerServing!.toInt()} kcal' : '계산 불가'),
          _infoChip(Icons.timer_outlined, AppTheme.textSecondary,
              '${recipe!.cookTimeMin}분'),
          _infoChip(Icons.signal_cellular_alt, AppTheme.textSecondary,
              '난이도 ${recipe!.difficultyDots}'),
          _infoChip(Icons.people_outline, AppTheme.textSecondary,
              '${recipe!.servings}인분'),
        ],
      ),
    );
  }

  Widget _infoChip(IconData icon, Color color, String text) {
    return Column(
      children: [
        Icon(icon, color: color, size: 24),
        const SizedBox(height: 4),
        Text(text, style: const TextStyle(fontSize: AppTheme.fontSmall, fontWeight: FontWeight.w500)),
      ],
    );
  }

  // ─── 조리순서 탭 (한 단계씩 큰 글씨) ───
  Widget _buildStepsTab() {
    final steps = recipe!.steps;
    if (steps.isEmpty) {
      return const Center(child: Text('조리 순서가 등록되지 않았습니다', style: TextStyle(fontSize: 18)));
    }

    return Column(
      children: [
        Expanded(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // 단계 번호
                Container(
                  width: 56, height: 56,
                  decoration: BoxDecoration(
                    color: AppTheme.primary,
                    borderRadius: BorderRadius.circular(28),
                  ),
                  child: Center(
                    child: Text(
                      '${_currentStep + 1}',
                      style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.white),
                    ),
                  ),
                ),
                const SizedBox(height: 24),

                // 조리 텍스트 (큰 글씨)
                Text(
                  steps[_currentStep]['text'] ?? '',
                  style: const TextStyle(fontSize: AppTheme.fontTitle, height: 1.6),
                  textAlign: TextAlign.center,
                ),

                const SizedBox(height: 16),
                Text(
                  '${_currentStep + 1} / ${steps.length}',
                  style: const TextStyle(fontSize: AppTheme.fontCaption, color: AppTheme.textSecondary),
                ),
              ],
            ),
          ),
        ),

        // 이전/다음 버튼
        Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: _currentStep > 0
                      ? () => setState(() => _currentStep--)
                      : null,
                  icon: const Icon(Icons.arrow_back, size: 24),
                  label: const Text('이전'),
                  style: OutlinedButton.styleFrom(minimumSize: const Size(0, 56)),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: _currentStep < steps.length - 1
                      ? () => setState(() => _currentStep++)
                      : null,
                  icon: const Icon(Icons.arrow_forward, size: 24),
                  label: Text(_currentStep < steps.length - 1 ? '다음' : '완료'),
                  style: ElevatedButton.styleFrom(minimumSize: const Size(0, 56)),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  // ─── 재료 탭 ───
  Widget _buildIngredientsTab() {
    if (ingredients == null || ingredients!.isEmpty) {
      return const Center(child: Text('재료 정보가 없습니다', style: TextStyle(fontSize: 18)));
    }

    return ListView.separated(
      padding: const EdgeInsets.all(16),
      itemCount: ingredients!.length,
      separatorBuilder: (_, __) => const Divider(height: 1),
      itemBuilder: (ctx, index) {
        final item = ingredients![index];
        final ing = item['ingredient'];
        final name = ing?['name_std'] ?? '알 수 없음';
        final qty = item['qty'];
        final unit = item['unit'] ?? '';
        final note = item['note'];
        final category = ing?['category'] ?? '기타';
        final catColor = AppTheme.categoryColors[category] ?? Colors.grey;

        return ListTile(
          contentPadding: const EdgeInsets.symmetric(vertical: 4),
          leading: Container(
            width: 8, height: 40,
            decoration: BoxDecoration(color: catColor, borderRadius: BorderRadius.circular(4)),
          ),
          title: Text(name, style: const TextStyle(fontSize: AppTheme.fontBody)),
          subtitle: note != null ? Text(note, style: const TextStyle(fontSize: AppTheme.fontSmall)) : null,
          trailing: Text(
            '$qty $unit',
            style: const TextStyle(fontSize: AppTheme.fontBody, fontWeight: FontWeight.bold),
          ),
        );
      },
    );
  }

  // ─── 영양정보 탭 ───
  Widget _buildNutritionTab() {
    final macros = recipe!.macrosPerServing;

    if (recipe!.kcalPerServing == null || macros == null) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.info_outline, size: 48, color: Colors.grey),
            SizedBox(height: 16),
            Text('영양 정보를 계산할 수 없습니다', style: TextStyle(fontSize: 18)),
            SizedBox(height: 8),
            Text('일부 재료의 정량 정보가 부족합니다', style: TextStyle(fontSize: 16, color: Colors.grey)),
          ],
        ),
      );
    }

    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        children: [
          // 칼로리 큰 표시
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: AppTheme.accent.withOpacity(0.1),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Column(
              children: [
                const Text('1인분 기준', style: TextStyle(fontSize: AppTheme.fontCaption, color: AppTheme.textSecondary)),
                const SizedBox(height: 8),
                Text(
                  '${recipe!.kcalPerServing!.toInt()} kcal',
                  style: const TextStyle(fontSize: 36, fontWeight: FontWeight.bold, color: AppTheme.accent),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          // 영양소 바
          _nutrientBar('탄수화물', macros['carb']?.toDouble() ?? 0, Colors.amber, 'g'),
          const SizedBox(height: 16),
          _nutrientBar('단백질', macros['protein']?.toDouble() ?? 0, Colors.red[400]!, 'g'),
          const SizedBox(height: 16),
          _nutrientBar('지방', macros['fat']?.toDouble() ?? 0, Colors.blue[400]!, 'g'),
          const SizedBox(height: 16),
          _nutrientBar('나트륨', macros['sodium']?.toDouble() ?? 0, Colors.purple[300]!, 'mg'),
        ],
      ),
    );
  }

  Widget _nutrientBar(String label, double value, Color color, String unit) {
    return Row(
      children: [
        SizedBox(
          width: 80,
          child: Text(label, style: const TextStyle(fontSize: AppTheme.fontCaption)),
        ),
        Expanded(
          child: ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: LinearProgressIndicator(
              value: (value / 200).clamp(0, 1),
              minHeight: 24,
              backgroundColor: Colors.grey[200],
              color: color,
            ),
          ),
        ),
        const SizedBox(width: 12),
        SizedBox(
          width: 80,
          child: Text(
            '${value.toStringAsFixed(1)} $unit',
            style: const TextStyle(fontSize: AppTheme.fontCaption, fontWeight: FontWeight.bold),
            textAlign: TextAlign.right,
          ),
        ),
      ],
    );
  }
}
