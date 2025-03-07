# meeting_summary
meeting summary application made by AI agent

# Instruction by human owner
## 機能
ソースコードはGithub、音声データや議事録テンプレートはユーザーがアップロード、プロンプトやLLMのAPIキーなどはユーザーがwebUIに入力します。 作成した議事録や質問応答データはダウンロードできます。
文字起こしはDeepgramまたはGroq APIのwhisper、要約はazure openAIのAPIまたはGroq APIのllama 3.3またはgemma-2を使用します。
Google colabratoryでgit cloneして、ウェブアプリを起動して使います。

## 注意
APIキーは安全性に配慮して、Google Colab のシークレット機能を利用してください。  音声データが長い場合分割して処理する必要があります。 文字起こしの要約もmap-reduceやrefine等を選択して行えます。
開発中のナレッジはgithub内の特定のフォルダで管理し、プログラマーが適宜参照できるようにしてください。
議事録テンプレートはテーブルが挿入されたワードファイルで提供されるため、レイアウトを読み取って対応する必要があります。（必要に応じてLLMを利用します）
