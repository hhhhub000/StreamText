# StreamText

PCで再生されている音声をリアルタイムで文字起こしし、話者ごとに発言を分離して表示するデスクトップアプリケーションです。

This is a desktop application that performs real-time transcription of your PC's audio output while separating speech by speaker.

---

## ✨ 主な機能 (Features)

* **リアルタイム文字起こし**: PCから出力されるあらゆる音声（YouTube、会議、ゲームなど）をリアルタイムでテキスト化します。
* **話者分離（ダイアライゼーション）**: `pyannote.audio` を利用して、複数の話者を識別し、誰の発言かを表示します。
* **高い汎用性**: ブラウザや特定のアプリに依存せず、システム音声全体を対象とします。

---

* **Real-time Transcription**: Transcribes any audio output from your PC (e.g., YouTube, online meetings, games) in real-time.
* **Speaker Diarization**: Utilizes `pyannote.audio` to identify different speakers and label their speech accordingly.
* **System-Wide**: Works on all system audio, independent of any specific browser or application.

---

## ⚙️ 動作環境 (Requirements)

* Python 3.9 以上
* [FFmpeg](https://ffmpeg.org/download.html)
* NVIDIA GPU (CUDA) を強く推奨（CPUでも動作しますが、非常に低速になる可能性があります）

---

* Python 3.9+
* [FFmpeg](https://ffmpeg.org/download.html)
* An NVIDIA GPU (CUDA) is strongly recommended (the app can run on a CPU, but it may be very slow).

---

## 🚀 インストール & セットアップ (Installation & Setup)

#### 1. リポジトリをクローン (Clone the Repository)

```bash
git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git)
cd YOUR_REPOSITORY
```

#### 2. 必要なライブラリをインストール (Install Dependencies)

`requirements.txt` を使って、必要なPythonライブラリをまとめてインストールします。

Use `requirements.txt` to install all necessary Python libraries.

```bash
pip install -r requirements.txt
```
**Note:** `torch` (PyTorch) might require a specific installation command depending on your environment (especially if you have an NVIDIA GPU). Please refer to the [official PyTorch website](https://pytorch.org/get-started/locally/) for details.

#### 3. Hugging Face アクセストークンの準備 (Prepare Your Hugging Face Access Token)

このアプリケーションは `pyannote.audio` を利用するため、Hugging Faceのアクセストークンが必要です。

This application uses `pyannote.audio`, which requires a Hugging Face access token.

1.  [Hugging Face](https://huggingface.co/) にサインアップ（またはログイン）します。/ Sign up or log in to [Hugging Face](https://huggingface.co/).
2.  [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1) と [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0) のモデルページにアクセスし、ライセンスに同意します。/ Visit the model pages for [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1) and [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0) and accept the user license agreements.
3.  [アクセストークンページ](https://huggingface.co/settings/tokens)で新しいトークン（Role: `read`）を作成し、コピーします。/ Go to your [Access Tokens page](https://huggingface.co/settings/tokens) to create a new token (Role: `read`) and copy it.

#### 4. 設定ファイルの作成 (Create the Configuration File)

`config.py.example` をコピーして `config.py` という名前のファイルを作成します。

Copy `config.py.example` to create a new file named `config.py`.

```bash
cp config.py.example config.py
```

作成した `config.py` ファイルをエディタで開き、`YOUR_HUGGINGFACE_TOKEN` の部分を、先ほど取得したご自身のHugging Faceアクセストークンに書き換えます。

Open the newly created `config.py` file and replace `YOUR_HUGGINGFACE_TOKEN` with the access token you copied from Hugging Face.

```python
# config.py
HF_TOKEN = "hf_xxxxxxxxxxxxxxxxxxxxxxxxxxx" # ← ここを書き換える / Replace this with your token
```

---

## ▶️ 使い方 (Usage)

以下のコマンドでアプリケーションを起動します。

Run the following command to launch the application.

```bash
python main_app.py
```

初回起動時は、AIモデル（Whisperとpyannote）のダウンロードが始まるため、数分かかることがあります。

On the first launch, the application will download the AI models (Whisper and pyannote), which may take several minutes.

---

## 🔧 設定のカスタマイズ (Configuration)

`config.py` を編集することで、アプリケーションの動作をカスタマイズできます。

You can customize the application's behavior by editing the `config.py` file.

* `WHISPER_MODEL`: 文字起こしモデルを変更できます (`tiny`, `base`, `small`など)。/ Changes the transcription model (e.g., `tiny`, `base`, `small`).
* `INTERVAL_SECONDS`: 音声を処理する間隔（秒）を調整できます。/ Adjusts the audio processing interval in seconds.
* `DEVICE`: `cuda` または `cpu` を明示的に指定できます。/ Explicitly set the device to `cuda` or `cpu`.

---

## 📄 ライセンス (License)

このプロジェクトは [MIT License](LICENSE) の下で公開されています。

This project is licensed under the [MIT License](LICENSE).

---

## 🙏 謝辞 (Acknowledgements)

このアプリケーションは、以下の素晴らしいプロジェクトによって実現されています。

This application is made possible by these incredible open-source projects:

* [OpenAI Whisper](https://github.com/openai/whisper)
* [pyannote.audio](https://github.com/pyannote/pyannote-audio)