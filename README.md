<img width="1230" height="606" alt="image" src="https://github.com/user-attachments/assets/e2033aec-8dcb-44af-a457-87d43fe371ca" />

# Qiita Stock Analyzer

こちらから試していただけます。  
👉[Qiita stock Analyzer ](https://qiita-stock-analyzer-nxhtleme4pley9wmqxfsrz.streamlit.app/)

> ストックしがちなQiita記事を分析して、自分の技術的関心の変化を可視化するアプリ

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 概要

Qiita Stock Analyzerは、Qiitaでストックした記事を分析し、年ごとの技術的関心の変化を可視化するWebアプリケーションです。自分がどんな技術に興味を持っているのか、その関心がどう変化してきたのかを直感的に理解できます。
というのは建前で「あとで読む」に次々に放り込んでいる記事から後回しにしていることを理解しよう、というアプリです。

## 主な機能

### 直近5年間のストック分析
過去5年間にストックしたQiita記事を自動で抽出し、分析します。

### 年別ストック数
どの年に最も多くの記事をストックしたかを一目で確認できます。学習意欲が高かった時期や、新しい技術に挑戦していた時期が見えてきます。

### ストックしがちな記事のタグランキング
全期間で最もストックした技術タグのTOP10をランキング形式で表示。金・銀・銅メダルで上位3つを強調表示します。

### タグのトレンド
複数のタグを選択して、年次推移を折れ線グラフで比較できます。特定の技術への関心の変化を追跡できます。

### 詳細データ
ストックした記事を年やタグでフィルタして確認できます。CSV形式でのエクスポートも可能です。

## セットアップ

### 必要な環境

- Python 3.12以上
- インターネット接続（Qiita APIへのアクセス）

### インストール

1. **リポジトリのクローン**

```bash
git clone https://github.com/yourusername/qiita-stock-analyzer.git
cd qiita-stock-analyzer
```

2. **仮想環境の作成（推奨）**

```bash
# Windowsの場合
python -m venv venv
venv\Scripts\activate

# macOS/Linuxの場合
python -m venv venv
source venv/bin/activate
```

3. **依存パッケージのインストール**

```bash
pip install -r requirements.txt
```

### Qiita アクセストークンの取得

1. [Qiitaアプリケーション設定ページ](https://qiita.com/settings/applications)にアクセス
2. 「新しいトークンを発行する」をクリック
3. トークンの説明を入力（例：「Stock Analyzer」）
4. スコープは **何も選択しない**（デフォルトで`read_qiita`が付与されます）
5. 「発行する」ボタンをクリック
6. 生成されたトークンをコピー（**このトークンは二度と表示されません**）

## 使い方

### アプリの起動

```bash
streamlit run app.py
```

ブラウザが自動的に開き、アプリが表示されます（通常は `http://localhost:8501`）。

### 分析の実行

1. サイドバーの「Qiita Access Token」入力欄にトークンを入力
2. 「分析開始」ボタンをクリック
3. プログレスバーで進捗を確認
4. 分析結果が自動的に表示されます

### 分析結果の見方

#### 基本統計
- **総ストック数**: 直近5年間のストック記事数
- **対象年数**: 分析対象の年数
- **ユニークタグ**: 記事に付けられたユニークなタグの数
- **期間**: 分析対象期間

#### グラフの操作
- **年別ストック数**: 各年のストック数を棒グラフで表示
- **タグランキング**: 🥇🥈🥉 メダルで上位3タグを強調表示
- **タグのトレンド**: 複数のタグを選択して比較可能

#### 詳細データ
- 年・タグでフィルタリング可能
- CSVファイルとしてエクスポート可能
- 記事タイトル、URL、いいね数を表示

## 技術スタック

- **[Streamlit](https://streamlit.io/)** - Webアプリケーションフレームワーク
- **[Plotly](https://plotly.com/python/)** - インタラクティブなグラフ可視化
- **[Requests](https://requests.readthedocs.io/)** - Qiita API通信
- **[Python 3.12+](https://www.python.org/)** - 開発言語

## ファイル構成

```
qiita-stock-analyzer/
├── app.py                 # メインアプリケーション
├── requirements.txt       # 依存パッケージ一覧
├── README.md             # このファイル
├── QUICKSTART.md         # クイックスタートガイド
├── LICENSE               # ライセンス情報
└── .gitignore            # Git除外設定
```

## 開発

### 開発プロセス
1. **要件定義**: どんな情報を可視化したいかを整理
2. **API調査**: Qiita API v2の仕様を調査
3. **プロトタイプ**: 基本的なデータ取得と表示機能を実装
4. **UI/UX改善**: ユーザーフィードバックを元に段階的に改善
5. **パフォーマンス最適化**: データ処理とグラフ表示を最適化

### 直面した課題と解決策

#### 1. SSL証明書エラー
**課題**: 企業プロキシ環境でSSL証明書の検証エラーが発生  
**解決**: SSL検証をデフォルトで無効化（企業環境での利用を考慮）

#### 2. API 404エラー
**課題**: 初期の実装で404エラーが頻発  
**解決**: `authenticated_user`エンドポイントでuser_idを取得してから、`users/{user_id}/stocks`でストックを取得

#### 3. データ量が多い
**課題**: 全期間のストックを取得すると表示が重くなる  
**解決**: 直近5年間に限定して分析

#### 4. UI状態の保持
**課題**: フィルタ操作時に画面がリセットされる  
**解決**: `st.session_state`を活用して状態を保持

## 注意事項

### API利用制限
- Qiita APIには利用制限があります
- 大量のストックがある場合、取得に時間がかかることがあります

### セキュリティ
- **アクセストークンは第三者に共有しないでください**
- トークンの権限は`read_qiita`のみで十分です
- GitHubにプッシュする際は`.env`ファイルなどにトークンを保存し、`.gitignore`に追加してください

### パフォーマンス
- 初回分析時は全データを取得するため、ストック数に応じて数秒〜数十秒かかります
- セッション中はデータがキャッシュされるため、2回目以降は高速です

## コントリビューション

バグ報告や機能追加の提案は [Issue](https://github.com/yutowac/qiita-stock-analyzer/issues) でお願いします。

プルリクエストも歓迎します！

### 開発環境のセットアップ

1. リポジトリをフォーク
2. ローカルにクローン
3. 仮想環境を作成してパッケージをインストール
4. 修正・機能追加を実装
5. プルリクエストを作成

## ライセンス

MIT License - 詳細は [LICENSE](LICENSE) ファイルを参照してください。

## 謝辞

- [Qiita API v2](https://qiita.com/api/v2/docs) - データ提供
- [Streamlit](https://streamlit.io/) - アプリケーションフレームワーク
- [Plotly](https://plotly.com/) - グラフ可視化ライブラリ

## お問い合わせ

質問や提案がある場合は、[Issue](https://github.com/yutowac/qiita-stock-analyzer/issues)を作成してください。

---

