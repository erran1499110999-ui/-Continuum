"""python -m continuity.webui 启动入口（仅绑定 127.0.0.1）。

用法：
  python -m continuity.webui [--port 8777] [--no-browser]
默认端口 8777（原默认 8765 在开发机被百度输入法等常驻程序占用，经创始人裁决改为 8777）。
"""
from __future__ import annotations

import argparse
import sys
import webbrowser
from typing import List, Optional

from .server import WebUIServer


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m continuity.webui",
        description="Continuity Studio 本地 Web UI（仅绑定 127.0.0.1，不上传任何数据）",
    )
    parser.add_argument("--port", type=int, default=8777, help="监听端口（默认 8777）")
    parser.add_argument(
        "--no-browser", action="store_true", help="启动后不自动打开浏览器"
    )
    args = parser.parse_args(argv)

    try:
        server = WebUIServer(port=args.port)
    except OSError as exc:
        print(f"错误: 无法监听 127.0.0.1:{args.port}（{exc}）", file=sys.stderr)
        return 2

    print(f"Continuity Studio 本地 Web UI: http://127.0.0.1:{server.port}/")
    print("仅供本机使用；本工具不上传任何角色数据。按 Ctrl+C 退出。")
    if not args.no_browser:
        try:
            webbrowser.open(f"http://127.0.0.1:{server.port}/")
        except Exception:
            pass  # 沙箱等环境可能无法打开浏览器：忽略，用户可手动访问

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n正在关闭…")
    finally:
        server.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
