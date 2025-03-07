audio-transcription-app/
├── README.md                     # プロジェクトの説明と使用方法
├── requirements.txt              # 必要なPythonパッケージ
├── app.py                        # メインアプリケーションエントリーポイント
├── run_in_colab.ipynb            # Google Colabで実行するためのノートブック
├── static/                       # 静的ファイル
│   ├── css/                      # スタイルシート
│   └── js/                       # JavaScriptファイル
├── templates/                    # HTMLテンプレート
├── src/                          # ソースコード
│   ├── api/                      # API連携モジュール
│   │   ├── __init__.py
│   │   ├── deepgram_client.py    # Deepgram API連携
│   │   ├── groq_client.py        # Groq API連携
│   │   └── azure_client.py       # Azure OpenAI API連携
│   ├── services/                 # サービス層
│   │   ├── __init__.py
│   │   ├── transcription.py      # 文字起こしサービス
│   │   ├── summarization.py      # 要約サービス
│   │   ├── qa_service.py         # Q&Aサービス
│   │   └── template_processor.py # テンプレート処理サービス
│   ├── utils/                    # ユーティリティ
│   │   ├── __init__.py
│   │   ├── audio_splitter.py     # 音声分割ユーティリティ
│   │   ├── file_utils.py         # ファイル操作ユーティリティ
│   │   └── security.py           # セキュリティユーティリティ（APIキー管理等）
│   └── models/                   # データモデル
│       ├── __init__.py
│       └── document.py           # 文書データモデル
└── knowledge/                    # 開発ナレッジベース
    ├── prompts/                  # LLMプロンプトテンプレート
    │   ├── summarization/        # 要約用プロンプト
    │   └── qa/                   # Q&A用プロンプト
    ├── templates/                # 議事録テンプレート例
    └── docs/                     # 開発ドキュメント
