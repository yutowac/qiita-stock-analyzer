# クイックスタートガイド

このガイドに従って、すぐにアプリを起動できます。

## ステップ1: パッケージのインストール

### 仮想環境の作成（推奨）

Windows PowerShellの場合：

```powershell
# プロジェクトフォルダに移動
cd C:\Users\WACHI.YUTO.P\Desktop\qiita-stock-analyzer

# Python 3.12で仮想環境を作成
py -3.12 -m venv venv312

# 実行ポリシーを設定（必要な場合）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# 仮想環境を有効化
.\venv312\Scripts\Activate.ps1
```

macOS/Linuxの場合：

```bash
cd ~/Desktop/qiita-stock-analyzer
python3 -m venv venv
source venv/bin/activate
```

### パッケージのインストール

```bash
# タイムアウトを延長してインストール
pip install --timeout 240 streamlit plotly requests
```

## ステップ2: Qiitaアクセストークンの取得

1. ブラウザで https://qiita.com/settings/applications を開く
2. 「新しいトークンを発行する」をクリック
3. トークンの説明を入力（例: Stock Analyzer）
4. スコープは何も選択しない（デフォルトで`read_qiita`が付与されます）
5. 「発行する」ボタンをクリック
6. 表示されたトークンをコピーして保存（二度と表示されません）

## ステップ3: アプリの起動

仮想環境を有効化した状態で：

```bash
streamlit run app.py
```

自動的にブラウザが開きます（http://localhost:8501）

## ステップ4: 分析の実行

1. サイドバーにコピーしたアクセストークンを貼り付け
2. 「分析開始」ボタンをクリック
3. データの取得と分析が自動実行されます
4. グラフやデータを確認

## 便利な使い方

### タグのトレンド分析
- 「タグのトレンド」セクションで、複数のタグを選択して比較
- 自分の関心の変化が一目瞭然

### 詳細データのフィルタリング
- 「詳細データを表示」セクションで年やタグでフィルタ
- 特定の技術に関する記事だけを抽出

### CSVエクスポート
- CSVダウンロードボタンで分析結果を保存
- Excelなどで追加の分析も可能

## トラブルシューティング

### パッケージのインストールエラー

ネットワークタイムアウトの場合：

```bash
# タイムアウト時間を延長
pip install --timeout 300 streamlit plotly requests

# 個別にインストール
pip install streamlit
pip install plotly
pip install requests
```

### アプリが起動しない

```bash
# Streamlitのバージョン確認
streamlit --version

# 再インストール
pip uninstall streamlit
pip install streamlit
```

### SSL証明書エラー

アプリは企業プロキシ環境に対応しており、デフォルトでSSL検証を無効化しています。それでもエラーが出る場合は、ネットワーク管理者に相談してください。

### データが取得できない（401エラー）

- アクセストークンが正しいか確認
- Qiitaにログインしているか確認
- トークンを再生成してみる

## 次回以降の起動方法

```powershell
# Windows
cd C:\Users\WACHI.YUTO.P\Desktop\qiita-stock-analyzer
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv312\Scripts\Activate.ps1
streamlit run app.py
```

```bash
# macOS/Linux
cd ~/Desktop/qiita-stock-analyzer
source venv/bin/activate
streamlit run app.py
```

## アプリの停止

ターミナルで `Ctrl+C` を押してください。

---

