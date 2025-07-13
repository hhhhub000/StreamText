import sys
import threading
import numpy as np
import soundcard as sc
import whisper
import torch
from pyannote.audio import Pipeline
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget,
    QMessageBox
)
from PySide6.QtCore import Signal, QObject

# 設定ファイルをインポート
import config

# --- バックグラウンド処理とUIを繋ぐためのクラス ---
class SignalEmitter(QObject):
    text_received = Signal(str)
    error_received = Signal(str)

class DiarizationWorker(threading.Thread):
    def __init__(self, hf_token, model_name, device_str, interval, mic_name=None):
        super().__init__()
        self.hf_token = hf_token
        self.model_name = model_name
        self.device_str = device_str  # whisper用
        self.device = torch.device(device_str)  # pyannote用
        self.interval_seconds = interval
        self.emitter = SignalEmitter()
        self._stop_event = threading.Event()
        self.sample_rate = 16000
        self.mic_name = mic_name

    def run(self):
        try:
            self.emitter.text_received.emit("モデルをロード中...\n")
            whisper_model = whisper.load_model(self.model_name, device=self.device_str)
            diarization_pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1", use_auth_token=self.hf_token
            ).to(self.device)
            self.emitter.text_received.emit("モデルのロード完了。文字起こしを開始します。\n")

            # 録音デバイスの選択
            if self.mic_name:
                mic_dev = sc.get_microphone(id=self.mic_name, include_loopback=True)
            else:
                mic_dev = sc.get_microphone(id=str(sc.default_speaker().name), include_loopback=True)

            with mic_dev.recorder(samplerate=self.sample_rate) as mic:
                while not self._stop_event.is_set():
                    audio_data = mic.record(numframes=self.sample_rate * self.interval_seconds)
                    # モノラル変換
                    if audio_data.ndim > 1:
                        audio_data = np.mean(audio_data, axis=1)
                    audio_tensor = torch.from_numpy(audio_data).float().to(self.device)
                    diarization_input = {"waveform": audio_tensor.unsqueeze(0), "sample_rate": self.sample_rate}
                    diarization = diarization_pipeline(diarization_input)

                    audio_np = audio_data.astype(np.float32)
                    transcription_result = whisper_model.transcribe(audio_np, fp16=False, language="ja", word_timestamps=True)

                    if not transcription_result["segments"]: continue

                    word_timestamps = [word for segment in transcription_result['segments'] for word in segment['words']]
                    speaker_texts = {}
                    for segment, _, speaker in diarization.itertracks(yield_label=True):
                        if speaker not in speaker_texts: speaker_texts[speaker] = []
                        words_in_segment = [wt['word'] for wt in word_timestamps if wt['start'] >= segment.start and wt['end'] <= segment.end]
                        if words_in_segment:
                            speaker_texts[speaker].append("".join(words_in_segment))
                    output_text = "".join(f"[{speaker}]: {' '.join(texts)}\n" for speaker, texts in speaker_texts.items() if texts)
                    if output_text:
                        self.emitter.text_received.emit(output_text)
        except Exception as e:
            self.emitter.error_received.emit(f"エラーが発生しました:\n{e}")

    def stop(self):
        self._stop_event.set()

# --- メインウィンドウ ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("話者分離リアルタイム文字起こし")
        self.setGeometry(100, 100, 700, 500)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.start_button = QPushButton("文字起こし開始")
        self.stop_button = QPushButton("停止")
        self.stop_button.setEnabled(False)

        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.start_button.clicked.connect(self.start_transcription)
        self.stop_button.clicked.connect(self.stop_transcription)
        self.worker = None

    def start_transcription(self):
        if config.HF_TOKEN == "YOUR_HUGGINGFACE_TOKEN" or not config.HF_TOKEN:
            QMessageBox.critical(self, "トークンエラー", "config.pyファイルにHugging Faceのアクセストークンを設定してください。")
            return
        self.text_edit.clear()
        device = config.DEVICE
        if device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"
        # 利用可能な録音デバイス一覧を取得
        mic_list = sc.all_microphones(include_loopback=True)
        mic_names = [mic.name for mic in mic_list]
        # ステレオミキサーや仮想ケーブルがあれば自動選択、なければデフォルト
        preferred = [name for name in mic_names if "stereo mix" in name.lower() or "cable" in name.lower()]
        mic_name = preferred[0] if preferred else None
        self.worker = DiarizationWorker(
            hf_token=config.HF_TOKEN,
            model_name=config.WHISPER_MODEL,
            device_str=device,
            interval=config.INTERVAL_SECONDS,
            mic_name=mic_name
        )
        self.worker.emitter.text_received.connect(self.update_text)
        self.worker.emitter.error_received.connect(self.show_error)
        self.worker.start()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_transcription(self):
        if self.worker:
            self.worker.stop()
            self.worker.join()
            self.worker = None
        self.text_edit.append("\n--- 停止しました ---")
        # ファイル出力処理
        text = self.text_edit.toPlainText()
        import datetime
        filename = f"transcription_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(text)
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
    def update_text(self, text):
        self.text_edit.append(text)
        
    def show_error(self, error_text):
        self.text_edit.append(f"\n--- エラー ---\n{error_text}")
        self.stop_transcription()

    def closeEvent(self, event):
        self.stop_transcription()
        event.accept()

# --- アプリケーションの実行 ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())