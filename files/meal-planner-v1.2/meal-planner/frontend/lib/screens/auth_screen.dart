import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/app_state.dart';
import '../theme/app_theme.dart';

class AuthScreen extends StatefulWidget {
  final ApiService api;
  final Function(Map<String, dynamic>) onLoginSuccess;

  const AuthScreen({super.key, required this.api, required this.onLoginSuccess});

  @override
  State<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends State<AuthScreen> {
  bool _isLogin = true; // true: 로그인, false: 회원가입
  bool _loading = false;
  String? _error;

  final _emailCtrl = TextEditingController();
  final _passwordCtrl = TextEditingController();
  final _nameCtrl = TextEditingController();
  final _birthYearCtrl = TextEditingController();
  final _heightCtrl = TextEditingController();
  final _weightCtrl = TextEditingController();
  String _sex = 'F';
  int _activity = 2;

  @override
  void dispose() {
    _emailCtrl.dispose();
    _passwordCtrl.dispose();
    _nameCtrl.dispose();
    _birthYearCtrl.dispose();
    _heightCtrl.dispose();
    _weightCtrl.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    setState(() { _loading = true; _error = null; });
    try {
      Map<String, dynamic> result;
      if (_isLogin) {
        result = await widget.api.login(
          email: _emailCtrl.text.trim(),
          password: _passwordCtrl.text,
        );
      } else {
        result = await widget.api.signup(
          email: _emailCtrl.text.trim(),
          password: _passwordCtrl.text,
          name: _nameCtrl.text.trim(),
          birthYear: int.tryParse(_birthYearCtrl.text),
          sex: _sex,
          heightCm: double.tryParse(_heightCtrl.text),
          weightKg: double.tryParse(_weightCtrl.text),
          activityLevel: _activity,
        );
      }
      widget.onLoginSuccess(result);
    } catch (e) {
      setState(() { _error = e.toString().replaceAll('Exception: ', ''); });
    } finally {
      setState(() { _loading = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 40),
              // 앱 로고
              Icon(Icons.restaurant_menu, size: 64, color: AppTheme.primary),
              const SizedBox(height: 12),
              Text('식단 플래너',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold,
                    color: AppTheme.primary)),
              const SizedBox(height: 8),
              Text(_isLogin ? '로그인하세요' : '회원가입',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 16, color: Colors.grey[600])),
              const SizedBox(height: 32),

              // 이메일
              _buildField(_emailCtrl, '이메일', Icons.email, TextInputType.emailAddress),
              const SizedBox(height: 12),

              // 비밀번호
              _buildField(_passwordCtrl, '비밀번호', Icons.lock, TextInputType.text, obscure: true),
              const SizedBox(height: 12),

              // 회원가입 추가 필드
              if (!_isLogin) ...[
                _buildField(_nameCtrl, '이름', Icons.person, TextInputType.text),
                const SizedBox(height: 12),
                Row(children: [
                  Expanded(child: _buildField(_birthYearCtrl, '출생년도', Icons.cake,
                      TextInputType.number)),
                  const SizedBox(width: 12),
                  Expanded(child: _buildDropdown()),
                ]),
                const SizedBox(height: 12),
                Row(children: [
                  Expanded(child: _buildField(_heightCtrl, '키(cm)', Icons.height,
                      TextInputType.number)),
                  const SizedBox(width: 12),
                  Expanded(child: _buildField(_weightCtrl, '체중(kg)',
                      Icons.monitor_weight, TextInputType.number)),
                ]),
                const SizedBox(height: 12),
                _buildActivitySelector(),
              ],

              const SizedBox(height: 20),

              // 에러 메시지
              if (_error != null)
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.red[50],
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(_error!, style: TextStyle(color: Colors.red[700], fontSize: 14)),
                ),

              const SizedBox(height: 16),

              // 로그인/가입 버튼
              ElevatedButton(
                onPressed: _loading ? null : _submit,
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.primary,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                child: _loading
                    ? const SizedBox(height: 24, width: 24,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                    : Text(_isLogin ? '로그인' : '가입하기'),
              ),

              const SizedBox(height: 16),

              // 전환 버튼
              TextButton(
                onPressed: () => setState(() { _isLogin = !_isLogin; _error = null; }),
                child: Text(
                  _isLogin ? '계정이 없으신가요? 회원가입' : '이미 계정이 있으신가요? 로그인',
                  style: TextStyle(fontSize: 15, color: AppTheme.primary),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildField(TextEditingController ctrl, String label, IconData icon,
      TextInputType type, {bool obscure = false}) {
    return TextField(
      controller: ctrl,
      keyboardType: type,
      obscureText: obscure,
      style: const TextStyle(fontSize: 16),
      decoration: InputDecoration(
        labelText: label,
        prefixIcon: Icon(icon, size: 22),
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
        filled: true,
        fillColor: Colors.white,
        contentPadding: const EdgeInsets.symmetric(vertical: 16, horizontal: 16),
      ),
    );
  }

  Widget _buildDropdown() {
    return DropdownButtonFormField<String>(
      value: _sex,
      decoration: InputDecoration(
        labelText: '성별',
        prefixIcon: const Icon(Icons.wc, size: 22),
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
        filled: true, fillColor: Colors.white,
        contentPadding: const EdgeInsets.symmetric(vertical: 16, horizontal: 16),
      ),
      items: const [
        DropdownMenuItem(value: 'F', child: Text('여성')),
        DropdownMenuItem(value: 'M', child: Text('남성')),
      ],
      onChanged: (v) => setState(() => _sex = v!),
    );
  }

  Widget _buildActivitySelector() {
    const labels = ['매우 적음', '적음', '보통', '많음', '매우 많음'];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('활동량', style: TextStyle(fontSize: 14, color: Colors.grey[700])),
        const SizedBox(height: 8),
        Row(
          children: List.generate(5, (i) {
            final level = i + 1;
            final selected = _activity == level;
            return Expanded(
              child: GestureDetector(
                onTap: () => setState(() => _activity = level),
                child: Container(
                  margin: EdgeInsets.only(right: i < 4 ? 6 : 0),
                  padding: const EdgeInsets.symmetric(vertical: 10),
                  decoration: BoxDecoration(
                    color: selected ? AppTheme.primary : Colors.white,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(
                      color: selected ? AppTheme.primary : Colors.grey[300]!),
                  ),
                  child: Text(labels[i],
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      fontSize: 11,
                      color: selected ? Colors.white : Colors.grey[700],
                      fontWeight: selected ? FontWeight.bold : FontWeight.normal,
                    )),
                ),
              ),
            );
          }),
        ),
      ],
    );
  }
}
