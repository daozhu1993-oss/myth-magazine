#!/usr/bin/env bash
cd "$(dirname "$0")"
echo "正在启动《神话》杂志本地服务器..."
python3 -m http.server 3456 --bind 127.0.0.1
