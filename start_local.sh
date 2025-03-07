#!/bin/bash

echo "音声文字起こし・要約Q&Aアプリケーション起動スクリプト (Mac/Linux用)"
echo ""

# Python実行ファイルの存在チェック
if ! command -v python3 &> /dev/null; then
    echo "エラー: Python3が見つかりません。"
    echo "Python3がインストールされているか確認してください。"
    exit 1
fi

# 仮想環境をチェック
if [ -d "venv" ]; then
    echo "仮想環境が見つかりました。"
    echo "仮想環境をアクティベートします..."
    source venv/bin/activate
else
    echo "仮想環境が見つかりません。"
    read -p "仮想環境を作成しますか？ (y/n): " create_venv
    if [ "$create_venv" = "y" ]; then
        echo "仮想環境を作成しています..."
        python3 -m venv venv
        if [ $? -ne 0 ]; then
            echo "仮想環境の作成に失敗しました。"
            exit 1
        fi
        source venv/bin/activate
    fi
fi

# 必要なパッケージのインストール確認
if ! pip show flask &> /dev/null; then
    echo "必要なパッケージをインストールしています..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "依存パッケージのインストールに失敗しました。"
        exit 1
    fi
fi

# アプリケーション実行
echo ""
echo "アプリケーションを起動しています..."
echo "ブラウザで http://localhost:5000 を開いてください。"
echo "終了するには Ctrl+C を押してください。"
echo ""

python3 run_local.py

exit 0
