import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/app_state.dart';
import '../models/models.dart';
import '../theme/app_theme.dart';

class ShoppingScreen extends StatefulWidget {
  const ShoppingScreen({super.key});

  @override
  State<ShoppingScreen> createState() => _ShoppingScreenState();
}

class _ShoppingScreenState extends State<ShoppingScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  bool _hideChecked = false;

  final List<String> _categories = ['전체', '채소', '육류', '해산물', '양념', '곡류', '유제품', '기타'];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: _categories.length, vsync: this);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<AppState>().loadShopping();
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<AppState>(
      builder: (context, state, _) {
        if (state.shoppingLoading) {
          return const Center(child: CircularProgressIndicator());
        }

        final items = state.shoppingItems;
        if (items.isEmpty) {
          return const Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.shopping_cart_outlined, size: 64, color: Colors.grey),
                SizedBox(height: 16),
                Text('장보기 리스트가 없습니다', style: TextStyle(fontSize: 18)),
                SizedBox(height: 8),
                Text('주간 메뉴를 먼저 생성해 주세요', style: TextStyle(fontSize: 16, color: Colors.grey)),
              ],
            ),
          );
        }

        // 통계
        final totalCount = items.length;
        final checkedCount = items.where((i) => i.checked).length;
        final pantryItems = items.where((i) => i.isPantry).toList();
        final buyItems = items.where((i) => !i.isPantry).toList();

        return Column(
          children: [
            // 상단 요약
            Container(
              padding: const EdgeInsets.all(16),
              color: AppTheme.primary.withOpacity(0.1),
              child: Row(
                children: [
                  const Icon(Icons.shopping_cart, color: AppTheme.primary, size: 28),
                  const SizedBox(width: 12),
                  Text(
                    '이번 주 장보기 ($checkedCount/$totalCount)',
                    style: const TextStyle(fontSize: AppTheme.fontBody, fontWeight: FontWeight.bold),
                  ),
                  const Spacer(),
                  // 체크한 항목 숨기기
                  TextButton.icon(
                    onPressed: () => setState(() => _hideChecked = !_hideChecked),
                    icon: Icon(_hideChecked ? Icons.visibility : Icons.visibility_off, size: 20),
                    label: Text(_hideChecked ? '전체 보기' : '완료 숨기기',
                      style: const TextStyle(fontSize: AppTheme.fontSmall)),
                  ),
                ],
              ),
            ),

            // 카테고리 탭
            TabBar(
              controller: _tabController,
              isScrollable: true,
              labelStyle: const TextStyle(fontSize: AppTheme.fontCaption, fontWeight: FontWeight.bold),
              unselectedLabelStyle: const TextStyle(fontSize: AppTheme.fontSmall),
              tabs: _categories.map((c) => Tab(text: c)).toList(),
            ),

            // 리스트
            Expanded(
              child: TabBarView(
                controller: _tabController,
                children: _categories.map((cat) {
                  List<ShoppingItemModel> filtered;
                  if (cat == '전체') {
                    filtered = items;
                  } else if (cat == '양념') {
                    filtered = pantryItems;
                  } else {
                    filtered = buyItems.where((i) => i.category == cat).toList();
                  }

                  if (_hideChecked) {
                    filtered = filtered.where((i) => !i.checked).toList();
                  }

                  if (filtered.isEmpty) {
                    return const Center(
                      child: Text('항목이 없습니다', style: TextStyle(fontSize: 16, color: Colors.grey)),
                    );
                  }

                  return ListView.separated(
                    padding: const EdgeInsets.all(16),
                    itemCount: filtered.length,
                    separatorBuilder: (_, __) => const Divider(height: 1),
                    itemBuilder: (ctx, index) {
                      final item = filtered[index];
                      return _buildShoppingItem(state, item);
                    },
                  );
                }).toList(),
              ),
            ),
          ],
        );
      },
    );
  }

  Widget _buildShoppingItem(AppState state, ShoppingItemModel item) {
    final catColor = AppTheme.categoryColors[item.category] ?? Colors.grey;

    return ListTile(
      contentPadding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      leading: Checkbox(
        value: item.checked,
        onChanged: (val) => state.toggleShoppingItem(item.id, val ?? false),
        activeColor: AppTheme.primary,
        materialTapTargetSize: MaterialTapTargetSize.padded,
      ),
      title: Text(
        item.ingredientName,
        style: TextStyle(
          fontSize: AppTheme.fontBody,
          fontWeight: FontWeight.w500,
          decoration: item.checked ? TextDecoration.lineThrough : null,
          color: item.checked ? Colors.grey : AppTheme.textPrimary,
        ),
      ),
      subtitle: item.isPantry
          ? const Text('🏠 상비 재료 (집에 있으면 체크)',
              style: TextStyle(fontSize: AppTheme.fontSmall, color: AppTheme.textSecondary))
          : null,
      trailing: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: catColor.withOpacity(0.15),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              item.displayQty,
              style: TextStyle(
                fontSize: AppTheme.fontCaption,
                fontWeight: FontWeight.bold,
                color: catColor,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
