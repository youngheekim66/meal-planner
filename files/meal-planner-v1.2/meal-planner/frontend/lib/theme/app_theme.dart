import 'package:flutter/material.dart';

/// 50~70대 최적화 테마
/// - 기본 16~18pt 이상
/// - 높은 대비
/// - 터치 영역 44px+
class AppTheme {
  // 브랜드 컬러
  static const Color primary = Color(0xFF2E7D32);      // 건강한 녹색
  static const Color primaryLight = Color(0xFF66BB6A);
  static const Color primaryDark = Color(0xFF1B5E20);
  static const Color accent = Color(0xFFFF8F00);        // 따뜻한 주황
  static const Color background = Color(0xFFF5F5F5);
  static const Color surface = Colors.white;
  static const Color error = Color(0xFFD32F2F);
  static const Color textPrimary = Color(0xFF212121);
  static const Color textSecondary = Color(0xFF616161);
  static const Color divider = Color(0xFFE0E0E0);

  // 칼로리 색상
  static const Color kcalGood = Color(0xFF43A047);
  static const Color kcalWarn = Color(0xFFFFA000);
  static const Color kcalOver = Color(0xFFE53935);

  // 카테고리 색상
  static const Map<String, Color> categoryColors = {
    '채소': Color(0xFF66BB6A),
    '육류': Color(0xFFEF5350),
    '해산물': Color(0xFF42A5F5),
    '양념': Color(0xFFFFCA28),
    '유제품': Color(0xFFAB47BC),
    '곡류': Color(0xFF8D6E63),
    '기타': Color(0xFF78909C),
  };

  // 글꼴 크기 (큰 글씨 모드)
  static const double fontTitle = 24;
  static const double fontHeading = 20;
  static const double fontBody = 18;
  static const double fontCaption = 16;
  static const double fontSmall = 14;

  static ThemeData get theme => ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.light(
      primary: primary,
      onPrimary: Colors.white,
      secondary: accent,
      onSecondary: Colors.white,
      surface: surface,
      onSurface: textPrimary,
      error: error,
    ),
    scaffoldBackgroundColor: background,
    appBarTheme: const AppBarTheme(
      backgroundColor: primary,
      foregroundColor: Colors.white,
      elevation: 0,
      centerTitle: true,
      titleTextStyle: TextStyle(
        fontSize: fontHeading,
        fontWeight: FontWeight.bold,
        color: Colors.white,
      ),
    ),
    // 큰 터치 영역
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        minimumSize: const Size(44, 52),
        textStyle: const TextStyle(fontSize: fontBody, fontWeight: FontWeight.w600),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        minimumSize: const Size(44, 52),
        textStyle: const TextStyle(fontSize: fontBody),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    ),
    cardTheme: CardTheme(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
    ),
    textTheme: const TextTheme(
      headlineLarge: TextStyle(fontSize: fontTitle, fontWeight: FontWeight.bold, color: textPrimary),
      headlineMedium: TextStyle(fontSize: fontHeading, fontWeight: FontWeight.bold, color: textPrimary),
      bodyLarge: TextStyle(fontSize: fontBody, color: textPrimary, height: 1.5),
      bodyMedium: TextStyle(fontSize: fontCaption, color: textSecondary, height: 1.4),
      labelLarge: TextStyle(fontSize: fontBody, fontWeight: FontWeight.w600, color: textPrimary),
    ),
    bottomNavigationBarTheme: const BottomNavigationBarThemeData(
      selectedItemColor: primary,
      unselectedItemColor: textSecondary,
      selectedLabelStyle: TextStyle(fontSize: fontCaption, fontWeight: FontWeight.w600),
      unselectedLabelStyle: TextStyle(fontSize: fontSmall),
      type: BottomNavigationBarType.fixed,
    ),
  );
}
