# widgets/__init__.py
from .login_window import LoginWindow
from .dashboard import Dashboard
from .transaction_window import TransactionWindow
from .report_window import ReportWindow
from .admin_window import AdminWindow
from .cash_window import CashWindow
from .user_management_window import UserManagementWindow
from .user_reports_window import UserReportsWindow
from .audit_log_window import AuditLogWindow
from .system_settings_window import SystemSettingsWindow

__all__ = [
    'LoginWindow',
    'Dashboard', 
    'TransactionWindow',
    'ReportWindow',
    'AdminWindow',
    'CashWindow'
]