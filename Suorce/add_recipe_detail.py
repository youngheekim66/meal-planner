# -*- coding: utf-8 -*-
"""
index.html에 레시피 상세보기 기능 추가
- 조리단계
- 영양정보 (칼로리/탄단지)
- YouTube 원본 링크
"""
import os

FILE = r"C:\Projects\meal-planner\backend\static\index.html"

# 1) 파일 읽기
with open(FILE, "r", encoding="utf-8") as f:
    html = f.read()

# 2) CSS 추가 (</style> 앞에)
detail_css = """
/* Recipe Detail Modal */
.recipe-detail-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 200; display: none; align-items: flex-end; justify-content: center; }
.recipe-detail-overlay.show { display: flex; }
.recipe-detail { background: white; width: 100%; max-width: 500px; max-height: 85vh; border-radius: 20px 20px 0 0; overflow-y: auto; padding: 24px 20px; animation: slideUp 0.3s ease; }
@keyframes slideUp { from { transform: translateY(100%); } to { transform: translateY(0); } }
.detail-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }
.detail-header h2 { font-size: 20px; font-weight: 700; flex: 1; }
.detail-close { background: none; border: none; font-size: 24px; cursor: pointer; color: #999; padding: 0 0 0 12px; }
.detail-tags { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 16px; }
.detail-tag { background: #E8F5E9; color: #2E7D32; font-size: 12px; padding: 4px 10px; border-radius: 12px; font-weight: 500; }
.detail-meta { display: flex; gap: 16px; margin-bottom: 20px; font-size: 13px; color: #666; }
.detail-section { margin-bottom: 20px; }
.detail-section-title { font-size: 15px; font-weight: 700; color: #2E7D32; margin-bottom: 10px; padding-bottom: 6px; border-bottom: 2px solid #E8F5E9; }
.nutrition-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
.nutrition-item { text-align: center; background: #F5F5F0; border-radius: 12px; padding: 12px 8px; }
.nutrition-value { font-size: 18px; font-weight: 700; color: #2E7D32; }
.nutrition-label { font-size: 11px; color: #666; margin-top: 2px; }
.step-item { display: flex; gap: 12px; margin-bottom: 12px; }
.step-num { width: 28px; height: 28px; background: #2E7D32; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 700; flex-shrink: 0; margin-top: 2px; }
.step-text { font-size: 14px; line-height: 1.6; color: #333; }
.youtube-btn { display: flex; align-items: center; justify-content: center; gap: 8px; width: 100%; padding: 14px; background: #FF0000; color: white; border: none; border-radius: 12px; font-size: 15px; font-weight: 700; font-family: inherit; cursor: pointer; text-decoration: none; margin-top: 8px; }
.youtube-btn:active { opacity: 0.9; transform: scale(0.98); }
"""

html = html.replace("</style>", detail_css + "</style>")

# 3) 모달 HTML 추가 (</body> 앞에)
detail_html = """
<!-- Recipe Detail Modal -->
<div id="recipeDetailOverlay" class="recipe-detail-overlay" onclick="closeRecipeDetail(event)">
  <div class="recipe-detail" onclick="event.stopPropagation()">
    <div id="recipeDetailContent"></div>
  </div>
</div>
"""

html = html.replace("</body>", detail_html + "</body>")

# 4) JS 함수 추가 (</script> 앞에)
detail_js = """

// ── Recipe Detail ──
function showRecipeDetail(recipeId) {
  var recipe = allRecipes.find(function(r) { return r.id === recipeId; });
  if (!recipe) return;

  var emojiMap = {
    '죽': '🥣', '국': '🍲', '찌개': '🫕', '볶음': '🍳', '조림': '🍖',
    '찜': '🫕', '면류': '🍜', '밥': '🍚', '간편식': '🥪', '반찬': '🥗',
    '나물': '🥬', '쌈': '🥬', '구이': '🥩', '전': '🥞', '덮밥': '🍛'
  };

  var emoji = '🍽️';
  if (recipe.tags) {
    for (var i = 0; i < recipe.tags.length; i++) {
      if (emojiMap[recipe.tags[i]]) { emoji = emojiMap[recipe.tags[i]]; break; }
    }
  }

  var cuisine = recipe.cuisine === 'KOREAN' ? '한식' : '자유';
  var stars = '';
  for (var j = 0; j < (recipe.difficulty || 1); j++) stars += '⭐';

  var html = '';
  html += '<div class="detail-header">';
  html += '<h2>' + emoji + ' ' + recipe.title + '</h2>';
  html += '<button class="detail-close" onclick="closeRecipeDetail()">&times;</button>';
  html += '</div>';

  // Tags
  if (recipe.tags && recipe.tags.length > 0) {
    html += '<div class="detail-tags">';
    recipe.tags.forEach(function(tag) {
      html += '<span class="detail-tag">#' + tag + '</span>';
    });
    html += '</div>';
  }

  // Meta
  html += '<div class="detail-meta">';
  html += '<span>' + cuisine + '</span>';
  html += '<span>⏱ ' + (recipe.cook_time_min || '?') + '분</span>';
  html += '<span>' + stars + '</span>';
  html += '<span>👥 ' + (recipe.servings || '?') + '인분</span>';
  html += '</div>';

  // Nutrition
  html += '<div class="detail-section">';
  html += '<div class="detail-section-title">📊 영양정보 (1인분)</div>';
  html += '<div class="nutrition-grid">';
  html += '<div class="nutrition-item"><div class="nutrition-value">' + (recipe.kcal_per_serving ? Math.round(recipe.kcal_per_serving) : '-') + '</div><div class="nutrition-label">kcal</div></div>';
  if (recipe.macros_per_serving) {
    html += '<div class="nutrition-item"><div class="nutrition-value">' + (recipe.macros_per_serving.carb || '-') + 'g</div><div class="nutrition-label">탄수화물</div></div>';
    html += '<div class="nutrition-item"><div class="nutrition-value">' + (recipe.macros_per_serving.protein || '-') + 'g</div><div class="nutrition-label">단백질</div></div>';
    html += '<div class="nutrition-item"><div class="nutrition-value">' + (recipe.macros_per_serving.fat || '-') + 'g</div><div class="nutrition-label">지방</div></div>';
  }
  html += '</div></div>';

  // Steps
  if (recipe.steps && recipe.steps.length > 0) {
    html += '<div class="detail-section">';
    html += '<div class="detail-section-title">👨‍🍳 조리단계</div>';
    recipe.steps.forEach(function(step) {
      html += '<div class="step-item">';
      html += '<div class="step-num">' + step.step + '</div>';
      html += '<div class="step-text">' + step.text + '</div>';
      html += '</div>';
    });
    html += '</div>';
  }

  // YouTube Link
  if (recipe.source_url && recipe.source_url.indexOf('youtube') >= 0) {
    html += '<div class="detail-section">';
    html += '<a href="' + recipe.source_url + '" target="_blank" class="youtube-btn">▶ YouTube 원본 영상 보기</a>';
    html += '</div>';
  }

  document.getElementById('recipeDetailContent').innerHTML = html;
  document.getElementById('recipeDetailOverlay').classList.add('show');
  document.body.style.overflow = 'hidden';
}

function closeRecipeDetail(event) {
  if (event && event.target !== event.currentTarget) return;
  document.getElementById('recipeDetailOverlay').classList.remove('show');
  document.body.style.overflow = '';
}
"""

html = html.replace("</script>", detail_js + "</script>")

# 5) renderRecipes에서 클릭 이벤트 추가
#    recipe-item에 onclick 추가
old_render = """'<div class="recipe-item">' +"""
new_render = """'<div class="recipe-item" onclick="showRecipeDetail(' + r.id + ')" style="cursor:pointer">' +"""

html = html.replace(old_render, new_render)

# 6) 저장 (UTF-8 with BOM for Windows)
with open(FILE, "w", encoding="utf-8-sig") as f:
    f.write(html)

print("[OK] index.html 수정 완료!")
print("  - 레시피 상세보기 모달 추가")
print("  - 조리단계, 영양정보, YouTube 링크")
print("")
print("다음 단계:")
print("  cd C:\\Projects\\meal-planner")
print("  git add .")
print('  git commit -m "feat: add recipe detail view"')
print("  git push")
