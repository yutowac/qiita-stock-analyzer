import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from collections import Counter, defaultdict

# ページ設定
st.set_page_config(page_title="Qiita Stock Analyzer", layout="wide")

# カスタムCSS - モダンなテックブログ風デザイン
st.markdown("""
<style>
    /* メインタイトルのスタイル */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 0.5rem;
        padding-bottom: 1rem;
        border-bottom: 3px solid #55c500;
    }
    
    .subtitle {
        font-size: 1.1rem;
        color: #7f8c8d;
        margin-bottom: 2rem;
    }
    
    /* セクションヘッダー */
    .section-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #34495e;
        margin-top: 1rem;
        margin-bottom: 0.8rem;
        padding-bottom: 0.3rem;
        border-bottom: 2px solid #ecf0f1;
    }
    
    /* メトリックカードのスタイリング */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    /* コンパクトなレイアウト */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* カード風スタイル */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* ボタンスタイル */
    .stButton>button {
        background-color: #55c500;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.6rem 2rem;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #4ab000;
        box-shadow: 0 4px 12px rgba(85, 197, 0, 0.3);
    }
    
    /* サイドバーのスタイル */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    
    [data-testid="stSidebar"] h1 {
        color: #2c3e50;
        font-size: 1.3rem;
        font-weight: 600;
    }
    
    /* 情報ボックス */
    .info-box {
        background-color: #e8f5e9;
        border-left: 4px solid #55c500;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    
    /* アクセストークン入力ボックスの枠線をグレーにする */
    [data-testid="stSidebar"] [data-testid="stTextInputRootElement"] {
        border: 2px solid #999 !important;
        border-radius: 4px;
    }
    
    [data-testid="stSidebar"] [data-testid="stTextInputRootElement"]:focus-within {
        border: 2px solid #55c500 !important;
        box-shadow: 0 0 0 2px rgba(85, 197, 0, 0.2);
    }
    
    /* 内側のinput要素の枠線を削除 */
    [data-testid="stSidebar"] input[type="password"] {
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# メインタイトル
st.markdown('<h1 class="main-title">Qiita Stock Analyzer</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">ストックしがちなQiita記事を分析します</p>', unsafe_allow_html=True)

# サイドバー: 設定
st.sidebar.header("設定")
access_token = st.sidebar.text_input(
    "Qiita Access Token", 
    type="password",
    help="Qiitaの個人用アクセストークンを入力してください"
)

# SSL検証はデフォルトで無効化（企業プロキシ環境対応）
disable_ssl_verify = True

# トークンテスト機能（デバッグ用・非表示）
if False and access_token and st.sidebar.button("トークンをテスト"):
    try:
        # ユーザー情報を取得してトークンが有効か確認
        test_url = "https://qiita.com/api/v2/authenticated_user"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(test_url, headers=headers, timeout=10, verify=not disable_ssl_verify)
        
        if response.status_code == 200:
            user_data = response.json()
            st.sidebar.success(f"トークン有効！\nユーザー: {user_data.get('id', 'Unknown')}")
        elif response.status_code == 401:
            st.sidebar.error("トークンが無効です。新しいトークンを生成してください。")
        else:
            st.sidebar.error(f"エラー {response.status_code}: {response.text}")
    except Exception as e:
        st.sidebar.error(f"接続エラー: {str(e)}")

st.sidebar.markdown("---")
st.sidebar.markdown("""
### アクセストークンの取得

[Qiitaアプリケーション設定ページ](https://qiita.com/settings/applications)でトークンを生成してください。
""")

with st.sidebar.expander("詳細な手順を表示"):
    st.markdown("""
    **手順:**
    1. 上記のリンクからQiitaアプリケーション設定ページを開く
    2. 「新しいトークンを発行する」をクリック
    3. 「read_qiita」スコープを選択
    4. 「発行する」をクリック
    5. 生成されたトークンをコピーして上記の入力欄に貼り付け
    
    **注意:** トークンは一度しか表示されないため、必ず保存してください。
    """)

# 分析開始ボタンをサイドバーに配置
analyze_button = st.sidebar.button("分析開始", type="primary", use_container_width=True)

def fetch_stocks(access_token, per_page=100, verify_ssl=True):
    """Qiitaのストック記事を取得"""
    stocks = []
    headers = {"Authorization": f"Bearer {access_token}"}
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # SSL警告を抑制
    if not verify_ssl:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # まず認証済みユーザーの情報を取得してuser_idを得る
    try:
        status_text.text("ユーザー情報を取得中...")
        user_response = requests.get(
            "https://qiita.com/api/v2/authenticated_user",
            headers=headers,
            timeout=10,
            verify=verify_ssl
        )
        
        if user_response.status_code != 200:
            if user_response.status_code == 401:
                st.error("アクセストークンが無効です。")
                st.info("新しいトークンを生成してください: https://qiita.com/settings/applications")
            else:
                st.error(f"ユーザー情報の取得に失敗: {user_response.status_code}")
            progress_bar.empty()
            status_text.empty()
            return None
        
        user_id = user_response.json()['id']
        st.toast(f"ユーザー: {user_id} のストックを取得します")
    except Exception as e:
        st.error(f"ユーザー情報の取得エラー: {str(e)}")
        return None
    
    # user_idを使ってストックを取得
    base_url = f"https://qiita.com/api/v2/users/{user_id}/stocks"
    page = 1
    
    while True:
        status_text.text(f"ページ {page} を取得中...")
        try:
            response = requests.get(
                base_url,
                headers=headers,
                params={"page": page, "per_page": per_page},
                timeout=10,
                verify=verify_ssl
            )
            
            if response.status_code != 200:
                if response.status_code == 404:
                    st.error(f"エラー 404: ストック情報が見つかりません")
                    st.info("ストックが0件の可能性があります。")
                else:
                    st.error(f"HTTPエラー {response.status_code}: {response.text}")
                break
            
            data = response.json()
            if not data:
                break
            
            stocks.extend(data)
            page += 1
            progress_bar.progress(min(page * 10 / 100, 1.0))
            
            # APIレート制限対策
            if len(data) < per_page:
                break
                
        except Exception as e:
            st.error(f"エラーが発生しました: {str(e)}")
            break
    
    progress_bar.empty()
    status_text.empty()
    return stocks

def process_stocks_data(stocks):
    """ストックデータを処理（直近5年間のみ）"""
    data = []
    current_year = datetime.now().year
    five_years_ago = current_year - 5
    
    for stock in stocks:
        try:
            created_at = datetime.strptime(stock['created_at'], '%Y-%m-%dT%H:%M:%S%z')
            
            # 直近5年間のデータのみ取得
            if created_at.year < five_years_ago:
                continue
                
            tags = [tag['name'] for tag in stock.get('tags', [])]
            
            data.append({
                'title': stock.get('title', ''),
                'url': stock.get('url', ''),
                'created_at': created_at,
                'year': created_at.year,
                'tags': tags,
                'likes_count': stock.get('likes_count', 0)
            })
        except Exception as e:
            continue
    
    return data

def analyze_by_year(data):
    """年ごとにタグを分析"""
    year_tags = defaultdict(Counter)
    for item in data:
        year = item['year']
        for tag in item['tags']:
            year_tags[year][tag] += 1
    
    return dict(year_tags)

def create_yearly_bar_chart(data):
    """年ごとのストック数の棒グラフ（コンパクト版）"""
    year_counts = Counter([item['year'] for item in data])
    years = sorted(year_counts.keys())
    counts = [year_counts[year] for year in years]
    
    # グラデーションカラー
    colors = ['rgba(85, 197, 0, ' + str(0.5 + (i / len(years)) * 0.5) + ')' for i in range(len(years))]
    
    fig = go.Figure(data=[
        go.Bar(x=years, y=counts, marker_color=colors,
               text=counts, textposition='outside')
    ])
    fig.update_layout(
        title='',
        xaxis_title='',
        yaxis_title='ストック数',
        showlegend=False
    )
    return fig

def create_tag_bar_chart(tags_counter, top_n, year):
    """タグの横棒グラフ（ランキング形式）"""
    top_tags = tags_counter.most_common(top_n)
    
    # ランキング形式でタグ名を作成（逆順にして下から上へ）
    tag_names = []
    tag_counts = []
    medal_emojis = {1: "🥇", 2: "🥈", 3: "🥉"}
    
    for i, (tag, count) in enumerate(reversed(top_tags), 1):
        rank = top_n - i + 1
        if rank <= 3:
            tag_name = f"{medal_emojis[rank]} {tag}"
        else:
            tag_name = f"{rank}位 {tag}"
        tag_names.append(tag_name)
        tag_counts.append(count)
    
    # グラデーションカラーを作成（上位ほど濃い色）
    colors = ['rgba(255, 99, 71, ' + str(0.4 + (i / top_n) * 0.6) + ')' for i in range(top_n)]
    
    fig = go.Figure(data=[
        go.Bar(y=tag_names, x=tag_counts, orientation='h', 
               marker_color=colors,
               text=tag_counts,
               textposition='outside')
    ])
    fig.update_layout(
        title='',
        xaxis_title='',
        yaxis_title='',
        height=max(450, len(tag_names) * 30),
        yaxis={'categoryorder': 'array', 'categoryarray': tag_names},
        showlegend=False
    )
    return fig

def display_detailed_data(data):
    """詳細データを表示する関数"""
    with st.expander("詳細データを表示", expanded=False):
        # フィルタ
        col1, col2 = st.columns(2)
        years = sorted(list(set([item['year'] for item in data])), reverse=True)
        all_tags = [tag for item in data for tag in item['tags']]
        
        with col1:
            # デフォルトを今年に設定
            current_year = datetime.now().year
            default_year = [current_year] if current_year in years else []
            filter_year = st.multiselect(
                "年でフィルタ",
                options=years,
                default=default_year
            )
        
        with col2:
            unique_tags = sorted(list(set(all_tags)))
            # AIタグがあればデフォルトに設定
            default_tag = "AI" if "AI" in unique_tags else "すべて"
            filter_tag = st.selectbox(
                "タグでフィルタ",
                options=["すべて"] + unique_tags,
                index=0 if default_tag == "すべて" else unique_tags.index(default_tag) + 1
            )
        
        # フィルタリング
        filtered_data = data
        if filter_year:
            filtered_data = [item for item in filtered_data if item['year'] in filter_year]
        if filter_tag != "すべて":
            filtered_data = [item for item in filtered_data if filter_tag in item['tags']]
        
        # データをソート
        filtered_data = sorted(filtered_data, key=lambda x: x['year'], reverse=True)
        
        # 表示件数とCSVダウンロードを上部に配置
        col_a, col_b = st.columns([3, 1])
        with col_a:
            st.write(f"**表示件数: {len(filtered_data)}件** （上限100件）")
        with col_b:
            # CSVエクスポート用データ生成
            csv_lines = ["年,タイトル,タグ,いいね数,URL"]
            for item in filtered_data:
                tags_str = '|'.join(item['tags'])
                csv_lines.append(f"{item['year']},\"{item['title']}\",\"{tags_str}\",{item['likes_count']},{item['url']}")
            csv_content = "\n".join(csv_lines)
            
            st.download_button(
                label="CSV",
                data=csv_content.encode('utf-8-sig'),
                file_name=f"qiita_stocks_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        # テーブル表示（コンパクト）
        for item in filtered_data[:100]:  # 最大100件表示
            col1, col2, col3 = st.columns([1, 6, 1])
            with col1:
                st.caption(f"**{item['year']}**")
            with col2:
                st.markdown(f"[{item['title']}]({item['url']})")
                if item['tags']:
                    st.caption(" ".join([f"`{tag}`" for tag in item['tags'][:5]]))
            with col3:
                st.caption(f"{item['likes_count']} いいね")
            st.divider()
        
        if len(filtered_data) > 100:
            st.info(f"残り {len(filtered_data) - 100} 件のデータがあります。CSVをダウンロードしてご確認ください。")

def create_trend_chart(year_tags, selected_tags, years):
    """タグのトレンド折れ線グラフ（コンパクト版）"""
    fig = go.Figure()
    
    # カラーパレット
    colors = ['#55c500', '#ff6b6b', '#4ecdc4', '#45b7d1', '#f7b731']
    
    for i, tag in enumerate(selected_tags):
        counts = [year_tags.get(year, Counter()).get(tag, 0) for year in years]
        fig.add_trace(go.Scatter(
            x=years, y=counts, mode='lines+markers',
            name=tag, line=dict(width=3, color=colors[i % len(colors)]),
            marker=dict(size=8)
        ))
    
    fig.update_layout(
        title='',
        xaxis_title='',
        yaxis_title='ストック数',
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    return fig

# セッション状態の初期化
if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = None

# メイン処理
if access_token:
    if analyze_button:
        # プログレスバーとステータステキストを準備
        progress_placeholder = st.empty()
        status_placeholder = st.empty()
        
        with progress_placeholder.container():
            progress_bar = st.progress(0)
            status_text = st.empty()
            status_text.text("ストック記事を取得中...")
        
        # fetch_stocks内でプログレスバーを使用
        stocks = fetch_stocks(access_token, verify_ssl=not disable_ssl_verify)
        
        # プログレスバーをクリア
        progress_placeholder.empty()
        status_placeholder.empty()
        
        if stocks:
            st.toast(f"{len(stocks)}件のストック記事を取得しました")
            
            # データ処理（プログレスバー表示）
            with st.spinner("データを処理中..."):
                data = process_stocks_data(stocks)
            
            if not data:
                st.warning("直近5年間のストックデータがありませんでした。")
                st.stop()
            
            st.toast(f"直近5年間（{datetime.now().year - 5}年以降）のデータを分析します")
            
            # セッション状態に保存
            st.session_state.analysis_data = {
                'data': data,
                'years': list(set([item['year'] for item in data])),
                'all_tags': [tag for item in data for tag in item['tags']],
                'year_tags': analyze_by_year(data)
            }
        elif stocks is not None:
            # stocksが空リストの場合（ストックが0件）
            st.warning("ストックが0件です。")
        # stocks is Noneの場合はfetch_stocks内でエラーメッセージが表示されている
    
    # 分析結果の表示（セッション状態から）
    if st.session_state.analysis_data:
        analysis = st.session_state.analysis_data
        data = analysis['data']
        years = analysis['years']
        all_tags = analysis['all_tags']
        year_tags = analysis['year_tags']
        
        # 基本統計（コンパクト）
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("総ストック数", len(data))
        with col2:
            st.metric("対象年数", f"{len(years)}年")
        with col3:
            st.metric("ユニークタグ", f"{len(set(all_tags))}個")
        with col4:
            st.metric("期間", f"{min(years)}-{max(years)}")
        
        st.markdown("---")
        
        # 2カラムレイアウトでコンパクト化
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("### 年別ストック数")
            yearly_chart = create_yearly_bar_chart(data)
            st.plotly_chart(yearly_chart, use_container_width=True)
        
        with col_right:
            st.markdown("### ストックしがちな記事のタグランキング")
            tags_counter = Counter(all_tags)
            tag_chart = create_tag_bar_chart(tags_counter, 10, "全期間")
            st.plotly_chart(tag_chart, use_container_width=True)
        
        # トレンドグラフ
        st.markdown("### タグのトレンド")
        
        # 全タグから上位10個を取得
        top_10_tags = [tag for tag, count in tags_counter.most_common(10)]
        
        selected_tags = st.multiselect(
            "トレンドを見たいタグを選択（最大5個推奨）",
            options=top_10_tags,
            default=top_10_tags[:3] if len(top_10_tags) >= 3 else top_10_tags
        )
        
        if selected_tags:
            trend_chart = create_trend_chart(year_tags, selected_tags, years)
            st.plotly_chart(trend_chart, use_container_width=True)
        else:
            st.info("タグを選択してトレンドを表示してください。")
        
        # 詳細データ
        display_detailed_data(data)

# 「このアプリでできること」は分析結果が表示されていない時のみ表示
if not st.session_state.analysis_data:
    if not access_token:
        st.markdown('<div class="info-box">サイドバーからQiitaのアクセストークンを入力してください</div>', unsafe_allow_html=True)
    
    # 説明セクション（分析結果が表示されるまで表示）
    st.markdown('<h2 class="section-header">このアプリでできること</h2>', unsafe_allow_html=True)
    st.markdown("""
    - **直近5年間のストック分析**
    - **年別ストック数**
    - **ストックしがちな記事のタグランキング**
    - **タグのトレンド**
    - **詳細データ**
    """)
    
    st.markdown('<h2 class="section-header">使い方</h2>', unsafe_allow_html=True)
    st.markdown("""
    1. [Qiitaアプリケーション設定ページ](https://qiita.com/settings/applications)でアクセストークンを生成
    2. サイドバーにトークンを入力
    3. 「分析開始」ボタンをクリック
    4. 分析結果を確認
    """)
