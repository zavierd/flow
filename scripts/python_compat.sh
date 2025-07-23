#!/bin/bash
# Python命令兼容性脚本
# 优先使用python3，fallback到python

if command -v python3 &> /dev/null; then
    exec python3 "$@"
elif command -v python &> /dev/null; then
    exec python "$@"
else
    echo "错误: 未找到Python解释器"
    exit 1
fi 