"""安全常量：不安全/不支持的文件扩展名清单（企划书 5.5）。

本工具对列入清单的文件只做隔离（复制、记录），绝不执行、不解析。
"""

from __future__ import annotations

# 可执行/二进制程序类（R3：隔离，绝不执行）
# 注意：本清单只增不减需谨慎——误判为安全会导致执行导入内容（规则 3）
EXECUTABLE_EXTENSIONS = frozenset(
    {".exe", ".bat", ".cmd", ".ps1", ".vbs", ".msi", ".scr", ".com", ".dll"}
)

# 脚本/宏/网页类（R3：隔离，绝不执行、不解析）
SCRIPT_EXTENSIONS = frozenset({".js", ".html", ".htm", ".py", ".sh", ".mjs", ".wsf", ".jar"})
