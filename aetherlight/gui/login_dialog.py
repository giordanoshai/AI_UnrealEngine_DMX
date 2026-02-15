from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QHBoxLayout
)
from aetherlight.database.auth_manager import get_auth_manager

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("登录 AetherLight Pro")
        self.setFixedSize(300, 200)
        
        self.auth_manager = get_auth_manager()
        
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout()
        
        # Email
        layout.addWidget(QLabel("邮箱:"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("user@example.com")
        layout.addWidget(self.email_input)
        
        # Password
        layout.addWidget(QLabel("密码:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.login_btn = QPushButton("登录")
        self.login_btn.clicked.connect(self._on_login)
        button_layout.addWidget(self.login_btn)
        
        self.register_btn = QPushButton("注册")
        self.register_btn.clicked.connect(self._on_register)
        button_layout.addWidget(self.register_btn)
        
        layout.addLayout(button_layout)
        
        # Status
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: red")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
    def _on_login(self):
        email = self.email_input.text()
        password = self.password_input.text()
        
        if not email or not password:
            self.status_label.setText("请输入邮箱和密码")
            return
            
        self.status_label.setText("登录中...")
        self.login_btn.setEnabled(False)
        
        try:
            user = self.auth_manager.sign_in(email, password)
            if user:
                self.accept()
            else:
                self.status_label.setText("登录失败: 邮箱或密码错误")
                self.login_btn.setEnabled(True)
        except Exception as e:
            self.status_label.setText(f"登录错误: {str(e)}")
            self.login_btn.setEnabled(True)
            
    def _on_register(self):
        email = self.email_input.text()
        password = self.password_input.text()
        
        if not email or not password:
            self.status_label.setText("请输入邮箱和密码")
            return
            
        self.status_label.setText("注册中...")
        self.register_btn.setEnabled(False)
        
        try:
            user = self.auth_manager.sign_up(email, password)
            if user:
                QMessageBox.information(self, "注册成功", "注册成功！请检查邮箱验证或直接登录。")
                self.status_label.setText("注册成功，请登录")
            else:
                self.status_label.setText("注册失败")
        except Exception as e:
            self.status_label.setText(f"注册错误: {str(e)}")
        finally:
            self.register_btn.setEnabled(True)
