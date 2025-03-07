##
# author   : Claude 3.7 Sonnet
# created  : 2025/03/07 15:33:30
##
import os
import tempfile
import gradio as gr
from src.services.transcription import TranscriptionService
from src.services.summarization import SummarizationService
from src.services.qa_service import QAService
from src.services.template_processor import TemplateProcessor
from src.utils.audio_splitter import AudioSplitter
from src.utils.file_utils import save_to_docx, get_allowed_audio_extensions
from src.utils.security import validate_api_keys

# サービスの初期化
transcription_service = TranscriptionService()
summarization_service = SummarizationService()
qa_service = QAService()
template_processor = TemplateProcessor()
audio_splitter = AudioSplitter()

def process_audio(
    audio_file, 
    template_file, 
    transcription_service_name,
    llm_service_name,
    summarization_method,
    deepgram_api_key=None,
    groq_api_key=None,
    azure_openai_key=None,
    azure_openai_endpoint=None,
    custom_prompt=None,
    max_audio_chunk_duration=600  # 10分（秒単位）
):
    """音声ファイルを処理し、文字起こしと要約を行う"""
    
    # APIキーの設定
    if deepgram_api_key:
        os.environ["DEEPGRAM_API_KEY"] = deepgram_api_key
    if groq_api_key:
        os.environ["GROQ_API_KEY"] = groq_api_key
    if azure_openai_key:
        os.environ["AZURE_OPENAI_KEY"] = azure_openai_key
    if azure_openai_endpoint:
        os.environ["AZURE_OPENAI_ENDPOINT"] = azure_openai_endpoint
    
    # APIキーの検証
    key_validation = validate_api_keys(transcription_service_name, llm_service_name)
    if not key_validation["valid"]:
        return None, None, key_validation["message"], None
    
    # 音声ファイルを一時ファイルとして保存
    temp_dir = tempfile.mkdtemp()
    temp_audio_path = os.path.join(temp_dir, "input_audio.wav")
    with open(temp_audio_path, "wb") as f:
        f.write(audio_file)
    
    # 音声ファイルが長い場合は分割
    audio_chunks = audio_splitter.split_audio(temp_audio_path, max_duration=max_audio_chunk_duration)
    
    # 文字起こし処理
    transcriptions = []
    for i, chunk_path in enumerate(audio_chunks):
        chunk_transcript = transcription_service.transcribe(
            chunk_path, 
            service=transcription_service_name
        )
        transcriptions.append(chunk_transcript)
    
    # 文字起こし結果を結合
    full_transcript = " ".join(transcriptions)
    
    # テンプレートの処理（存在する場合）
    template_structure = None
    if template_file:
        template_structure = template_processor.process_template(template_file)
    
    # 要約処理
    summary = summarization_service.summarize(
        full_transcript, 
        method=summarization_method,
        service=llm_service_name,
        custom_prompt=custom_prompt,
        template_structure=template_structure
    )
    
    # 文書化（Word形式）
    result_path = os.path.join(temp_dir, "transcription_summary.docx")
    save_to_docx(
        transcript=full_transcript, 
        summary=summary, 
        output_path=result_path,
        template_structure=template_structure
    )
    
    return full_transcript, summary, "処理が完了しました。", result_path

def answer_question(transcript, question, llm_service_name):
    """文字起こしに基づいて質問に回答する"""
    
    if not transcript:
        return "文字起こしが存在しません。まず音声ファイルを処理してください。"
    
    # APIキーの検証
    key_validation = validate_api_keys(None, llm_service_name)
    if not key_validation["valid"]:
        return key_validation["message"]
    
    # 質問応答処理
    answer = qa_service.answer(transcript, question, service=llm_service_name)
    return answer

def create_ui():
    """Gradioベースのユーザーインターフェイスを作成"""
    
    with gr.Blocks(title="音声文字起こし・要約アプリケーション") as app:
        gr.Markdown("# 音声文字起こし・要約アプリケーション")
        
        with gr.Tabs():
            with gr.TabItem("処理設定"):
                with gr.Row():
                    with gr.Column():
                        audio_file = gr.File(
                            label="音声ファイル", 
                            file_types=get_allowed_audio_extensions()
                        )
                        template_file = gr.File(
                            label="議事録テンプレート（オプション）", 
                            file_types=["docx"]
                        )
                        
                        transcription_service_name = gr.Radio(
                            label="文字起こしサービス",
                            choices=["deepgram", "groq_whisper"],
                            value="deepgram"
                        )
                        
                        llm_service_name = gr.Radio(
                            label="LLMサービス",
                            choices=["azure_openai", "groq_llama", "groq_gemma"],
                            value="azure_openai"
                        )
                        
                        summarization_method = gr.Radio(
                            label="要約方法",
                            choices=["map_reduce", "refine"],
                            value="map_reduce",
                            info="map_reduce: 分割して個別に要約した後に統合。refine: 順次要約を洗練していく方法。"
                        )
                        
                    with gr.Column():
                        with gr.Accordion("APIキー設定", open=False):
                            deepgram_api_key = gr.Textbox(
                                label="Deepgram APIキー", 
                                type="password",
                                info="Google Colabのシークレット機能を使用している場合は不要"
                            )
                            groq_api_key = gr.Textbox(
                                label="Groq APIキー", 
                                type="password",
                                info="Google Colabのシークレット機能を使用している場合は不要"
                            )
                            azure_openai_key = gr.Textbox(
                                label="Azure OpenAI APIキー", 
                                type="password",
                                info="Google Colabのシークレット機能を使用している場合は不要"
                            )
                            azure_openai_endpoint = gr.Textbox(
                                label="Azure OpenAI エンドポイント", 
                                info="Google Colabのシークレット機能を使用している場合は不要"
                            )
                        
                        with gr.Accordion("高度な設定", open=False):
                            custom_prompt = gr.Textbox(
                                label="カスタムプロンプト（オプション）", 
                                lines=5,
                                placeholder="LLMへのカスタムプロンプトを入力"
                            )
                            max_audio_chunk_duration = gr.Slider(
                                label="最大音声チャンク長（秒）",
                                minimum=60, 
                                maximum=1800, 
                                value=600,
                                step=60,
                                info="長い音声ファイルを分割する単位（秒）"
                            )
                
                process_button = gr.Button("処理開始", variant="primary")
                
            with gr.TabItem("結果"):
                status_text = gr.Textbox(label="ステータス", interactive=False)
                
                with gr.Tabs():
                    with gr.TabItem("文字起こし"):
                        transcript_output = gr.Textbox(
                            label="文字起こし結果", 
                            lines=20,
                            interactive=True
                        )
                    
                    with gr.TabItem("要約"):
                        summary_output = gr.Textbox(
                            label="要約結果", 
                            lines=20,
                            interactive=True
                        )
                    
                    with gr.TabItem("Q&A"):
                        question_input = gr.Textbox(
                            label="質問", 
                            placeholder="文字起こしの内容に基づいた質問を入力してください"
                        )
                        ask_button = gr.Button("質問する")
                        answer_output = gr.Textbox(label="回答", lines=10)
                        
                        ask_button.click(
                            fn=answer_question,
                            inputs=[transcript_output, question_input, llm_service_name],
                            outputs=answer_output
                        )
                
                result_file = gr.File(label="結果ファイル", interactive=False)
        
        process_button.click(
            fn=process_audio,
            inputs=[
                audio_file, 
                template_file, 
                transcription_service_name, 
                llm_service_name,
                summarization_method,
                deepgram_api_key,
                groq_api_key,
                azure_openai_key,
                azure_openai_endpoint,
                custom_prompt,
                max_audio_chunk_duration
            ],
            outputs=[
                transcript_output, 
                summary_output,
                status_text,
                result_file
            ]
        )
    
    return app

if __name__ == "__main__":
    app = create_ui()
    app.launch(server_name="0.0.0.0", server_port=7860)
