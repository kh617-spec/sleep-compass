import time
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components


# ==================================================
# ページ設定
# ==================================================
st.set_page_config(
    page_title="Sleep Compass",
    page_icon="🌙",
    layout="centered",
)


# ==================================================
# デザイン
# ==================================================
st.markdown(
    """
    <style>
    :root {
        color-scheme: light;
    }

    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #ffffff !important;
        color: #1f2937 !important;
    }

    .stApp {
        background:
            radial-gradient(circle at top right, #eef1ff 0%, transparent 35%),
            linear-gradient(180deg, #fafbff 0%, #ffffff 100%);
    }

    /* スマホのダークモードでも、白背景上の文字を濃色で固定 */
    .stApp p,
    .stApp li,
    .stApp label,
    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp h4,
    .stApp h5,
    .stApp h6,
    .stApp [data-testid="stMarkdownContainer"],
    .stApp [data-testid="stWidgetLabel"],
    .stApp [data-testid="stMetricLabel"],
    .stApp [data-testid="stMetricValue"] {
        color: #1f2937 !important;
    }

    .description-card,
    .advice-card,
    .insight-card {
        color: #1f2937 !important;
    }

    /* 濃い背景上は白文字を維持 */
    .hero-card,
    .hero-card *,
    .result-card,
    .result-card *,
    .stButton > button,
    .stButton > button *,
    .stFormSubmitButton > button,
    .stFormSubmitButton > button * {
        color: #ffffff !important;
    }

    .main .block-container {
        max-width: 900px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    .hero-card {
        padding: 2.2rem 2rem;
        border-radius: 24px;
        color: white;
        background: linear-gradient(135deg, #18234f 0%, #5067b3 100%);
        box-shadow: 0 14px 34px rgba(31, 45, 95, 0.20);
        margin-bottom: 1.5rem;
    }

    .hero-title {
        font-size: 2.7rem;
        font-weight: 800;
        margin: 0;
    }

    .hero-subtitle {
        margin-top: 0.7rem;
        font-size: 1.08rem;
        line-height: 1.8;
        opacity: 0.94;
    }

    .result-card {
        padding: 1.8rem;
        border-radius: 22px;
        color: white;
        text-align: center;
        background: linear-gradient(135deg, #202d65 0%, #566db9 100%);
        box-shadow: 0 14px 34px rgba(31, 45, 95, 0.20);
        margin: 1rem 0 1.5rem;
    }

    .description-card {
        padding: 1.2rem 1.3rem;
        border-radius: 16px;
        background: white;
        border: 1px solid #e4e7f0;
        margin-bottom: 1rem;
    }

    .advice-card {
        padding: 1rem 1.1rem;
        border-radius: 14px;
        background: #f5f7ff;
        border-left: 5px solid #5268b5;
        margin-bottom: 0.8rem;
    }

    .insight-card {
        padding: 0.9rem 1rem;
        border-radius: 12px;
        background: #f7f8fc;
        border: 1px solid #e4e7f0;
        margin-bottom: 0.7rem;
    }

    div[data-testid="stForm"] {
        padding: 1.3rem 1.4rem 1.6rem;
        border-radius: 20px;
        background-color: rgba(255,255,255,0.96);
        border: 1px solid #e3e6f0;
        box-shadow: 0 10px 28px rgba(31,45,95,0.07);
    }

    .stButton > button,
    .stFormSubmitButton > button {
        width: 100%;
        border-radius: 12px;
        border: none;
        padding: 0.8rem 1rem;
        font-weight: 700;
        color: white;
        background: linear-gradient(90deg, #27366f 0%, #5268b5 100%);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# タイプ情報
# ==================================================
TYPE_INFO = {
    0: {
        "name": "高疲労型",
        "icon": "😵",
        "image": "images/高疲労型.png",
        "count": 33,
        "percentage": 21.4,
        "description": (
            "起床時の疲労感や睡眠への不満が強く、改善したい気持ちはあるものの、"
            "ストレスや仕事・学習負担によって行動に移しにくい可能性があります。"
        ),
        "advice": [
            "寝る前に3分だけ呼吸を整えるなど、小さく始めましょう。",
            "夜に持ち越す作業量を減らすため、タスクを細分化しましょう。",
            "スマートフォンを寝室の外に置きましょう。",
        ],
    },
    1: {
        "name": "規則的生活型",
        "icon": "⏰",
        "image": "images/規則的生活型.png",
        "count": 23,
        "percentage": 14.9,
        "description": (
            "生活リズムや自己管理は比較的安定しています。"
            "ただし、仕事・家事・育児・介護などの外的要因が"
            "睡眠時間を制限している可能性があります。"
        ),
        "advice": [
            "家事や家庭内タスクの役割分担を見直しましょう。",
            "時短家電や外部サービスなどを検討しましょう。",
            "周囲へ協力を求めることも改善策に含めましょう。",
        ],
    },
    2: {
        "name": "良好睡眠型",
        "icon": "💤",
        "image": "images/良好睡眠型.png",
        "count": 61,
        "percentage": 39.6,
        "description": (
            "睡眠の質・量ともに比較的安定しています。"
            "現在の良い習慣を維持することが大切です。"
        ),
        "advice": [
            "現在の就寝・起床リズムを維持しましょう。",
            "自分に合っている良い習慣を言葉にして残しましょう。",
            "睡眠に関する正しい知識を学び、悪化を予防しましょう。",
        ],
    },
    3: {
        "name": "睡眠負債型",
        "icon": "🌙",
        "image": "images/睡眠負債型.png",
        "count": 37,
        "percentage": 24.0,
        "description": (
            "平日の睡眠不足を休日の寝だめで補い、"
            "夜更かしや睡眠先延ばしが習慣化しやすい傾向があります。"
        ),
        "advice": [
            "アプリ制限や自動ロックを設定しましょう。",
            "動画・ゲーム・SNSの時間を夜から夕方や移動時間へ移しましょう。",
            "休日の起床時刻を平日との差2時間以内に近づけましょう。",
        ],
    },
}

NAME_TO_ID = {info["name"]: type_id for type_id, info in TYPE_INFO.items()}

SIMPLE_PRIORITY = {
    "高疲労型": 4,
    "睡眠負債型": 3,
    "規則的生活型": 2,
    "良好睡眠型": 1,
}


# ==================================================
# 詳細診断用データ
# ==================================================
RAW_CLUSTER_CENTERS = np.array(
    [
        [2.758, 1.364, 1.242, 2.152, 1.576, 2.455, 2.242, 2.636, 4.091],
        [2.739, 0.348, 3.217, 3.565, 3.000, 2.957, 3.435, 3.261, 3.870],
        [3.508, 0.410, 1.344, 2.492, 3.230, 3.590, 2.607, 2.820, 4.262],
        [2.108, 1.838, 1.378, 2.568, 2.892, 3.432, 1.973, 1.892, 3.054],
    ],
    dtype=float,
)

STANDARDIZED_CLUSTER_CENTERS = np.array(
    [
        [-0.14, 0.42, -0.37, -0.45, -1.18, -0.76, -0.26, 0.01, 0.21],
        [-0.16, -0.60, 1.61, 0.97, 0.24, -0.26, 0.93, 0.64, -0.01],
        [0.61, -0.54, -0.27, -0.11, 0.47, 0.38, 0.11, 0.20, 0.39],
        [-0.79, 0.89, -0.23, -0.03, 0.13, 0.22, -0.53, -0.73, -0.82],
    ],
    dtype=float,
)

SLEEP_OPTIONS = [
    "5時間未満",
    "5時間以上6時間未満",
    "6時間以上7時間未満",
    "7時間以上8時間未満",
    "8時間以上",
]

SLEEP_SCORE_MAP = {option: index + 1 for index, option in enumerate(SLEEP_OPTIONS)}
SLEEP_HOURS_MAP = {
    "5時間未満": 4.5,
    "5時間以上6時間未満": 5.5,
    "6時間以上7時間未満": 6.5,
    "7時間以上8時間未満": 7.5,
    "8時間以上": 8.5,
}

SLEEP_DISPLAY_MAP = {
    "5時間未満": "5時間未満",
    "5時間以上6時間未満": "5〜6時間",
    "6時間以上7時間未満": "6〜7時間",
    "7時間以上8時間未満": "7〜8時間",
    "8時間以上": "8時間以上",
}


FATIGUE_OPTIONS = ["全くない", "あまりない", "普通", "ややある", "とてもある"]
FATIGUE_SCORE_MAP = {"全くない": 5, "あまりない": 4, "普通": 3, "ややある": 2, "とてもある": 1}

SATISFACTION_OPTIONS = ["とても不満", "やや不満", "普通", "やや満足", "とても満足"]
SATISFACTION_SCORE_MAP = {option: index + 1 for index, option in enumerate(SATISFACTION_OPTIONS)}

PHONE_OPTIONS = ["ほとんど使用しない", "週に1日程度", "週に2〜3日", "週に4〜5日", "ほぼ毎日"]
PHONE_SCORE_MAP = {"ほとんど使用しない": 5, "週に1日程度": 4, "週に2〜3日": 3, "週に4〜5日": 2, "ほぼ毎日": 1}

SCREEN_OPTIONS = ["2時間未満", "2時間以上4時間未満", "4時間以上6時間未満", "6時間以上8時間未満", "8時間以上"]
SCREEN_SCORE_MAP = {"2時間未満": 5, "2時間以上4時間未満": 4, "4時間以上6時間未満": 3, "6時間以上8時間未満": 2, "8時間以上": 1}

CHRONOTYPE_OPTIONS = ["かなり夜型", "夜型", "中間型", "朝型", "かなり朝型"]
CHRONOTYPE_SCORE_MAP = {option: index + 1 for index, option in enumerate(CHRONOTYPE_OPTIONS)}

POSTPONE_OPTIONS = ["全くしない", "あまりしない", "どちらともいえない", "ややする", "頻繁にする"]
POSTPONE_SCORE_MAP = {"全くしない": 5, "あまりしない": 4, "どちらともいえない": 3, "ややする": 2, "頻繁にする": 1}

PRIORITY_OPTIONS = ["全く優先していない", "あまり優先していない", "どちらともいえない", "やや優先している", "とても優先している"]
PRIORITY_SCORE_MAP = {option: index + 1 for index, option in enumerate(PRIORITY_OPTIONS)}

WANT_OPTIONS = ["全く思わない", "あまり思わない", "どちらともいえない", "思う", "強く思う"]
WANT_SCORE_MAP = {option: index + 1 for index, option in enumerate(WANT_OPTIONS)}

CAN_OPTIONS = ["全くできない", "あまりできない", "わからない", "ある程度できる", "十分できる"]
CAN_SCORE_MAP = {option: index + 1 for index, option in enumerate(CAN_OPTIONS)}



# ==================================================
# 共通関数
# ==================================================

def estimate_scaler_parameters() -> tuple[np.ndarray, np.ndarray]:
    means = []
    stds = []

    for column in range(RAW_CLUSTER_CENTERS.shape[1]):
        raw = RAW_CLUSTER_CENTERS[:, column]
        standardized = STANDARDIZED_CLUSTER_CENTERS[:, column]

        design = np.column_stack([standardized, np.ones_like(standardized)])
        slope, intercept = np.linalg.lstsq(design, raw, rcond=None)[0]

        means.append(float(intercept))
        stds.append(abs(float(slope)))

    return np.array(means), np.array(stds)


APPROX_MEANS, APPROX_STDS = estimate_scaler_parameters()


def diagnose_detail(user_values: list[float]) -> int:
    user_array = np.array(user_values, dtype=float)
    standardized_user = (user_array - APPROX_MEANS) / APPROX_STDS

    distances = np.linalg.norm(
        STANDARDIZED_CLUSTER_CENTERS - standardized_user,
        axis=1,
    )

    return int(np.argmin(distances))


def create_radar_chart(
    weekday_sleep_score: int,
    sleep_debt: float,
    phone_control: int,
    screen_balance: int,
    fatigue_recovery: int,
    satisfaction: int,
    bedtime_control: int,
    priority: int,
) -> go.Figure:
    rhythm_stability = max(1.0, min(5.0, 5.0 - sleep_debt))

    categories = [
        "睡眠時間",
        "リズム安定",
        "就寝前スマホ",
        "画面時間",
        "疲労回復",
        "睡眠満足度",
        "就寝管理",
        "睡眠優先度",
    ]

    values = [
        weekday_sleep_score,
        rhythm_stability,
        phone_control,
        screen_balance,
        fatigue_recovery,
        satisfaction,
        bedtime_control,
        priority,
    ]

    figure = go.Figure(
        go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill="toself",
            hovertemplate="%{theta}: %{r:.1f}点<extra></extra>",
        )
    )

    figure.update_layout(
        polar={
            "radialaxis": {
                "visible": True,
                "range": [0, 5],
                "tickvals": [1, 2, 3, 4, 5],
            }
        },
        showlegend=False,
        height=500,
        margin={"l": 60, "r": 60, "t": 40, "b": 40},
    )

    return figure



def create_comparison_radar_chart(result: dict) -> go.Figure:
    """本人と154名の近似平均を同じレーダーチャートに表示する。"""
    categories = [
        "睡眠時間",
        "リズム安定",
        "就寝前スマホ",
        "画面時間",
        "疲労回復",
        "睡眠満足度",
        "就寝管理",
        "睡眠優先度",
    ]

    user_values = [
        float(result["weekday_score"]),
        max(1.0, min(5.0, 5.0 - float(result["sleep_debt"]))),
        float(result["phone_control"]),
        float(result["screen_balance"]),
        float(result["fatigue_recovery"]),
        float(result["satisfaction"]),
        float(result["bedtime_control"]),
        float(result["priority"]),
    ]

    mean_values = [
        float(APPROX_MEANS[0]),
        max(1.0, min(5.0, 5.0 - float(APPROX_MEANS[1]))),
        float(APPROX_MEANS[2]),
        float(APPROX_MEANS[3]),
        float(APPROX_MEANS[4]),
        float(APPROX_MEANS[5]),
        float(APPROX_MEANS[7]),
        float(APPROX_MEANS[8]),
    ]

    figure = go.Figure()

    figure.add_trace(
        go.Scatterpolar(
            r=user_values + [user_values[0]],
            theta=categories + [categories[0]],
            fill="toself",
            name="あなた",
            hovertemplate="あなた：%{r:.1f}点<extra></extra>",
        )
    )

    figure.add_trace(
        go.Scatterpolar(
            r=mean_values + [mean_values[0]],
            theta=categories + [categories[0]],
            name="154名の近似平均",
            hovertemplate="平均：約%{r:.1f}点<extra></extra>",
        )
    )

    figure.update_layout(
        polar={
            "radialaxis": {
                "visible": True,
                "range": [0, 5],
                "tickvals": [1, 2, 3, 4, 5],
            }
        },
        showlegend=True,
        legend={"orientation": "h", "y": -0.12},
        height=520,
        margin={"l": 60, "r": 60, "t": 40, "b": 80},
    )

    return figure


def build_priority_items(result: dict) -> list[tuple[str, float, str]]:
    """改善優先度の高い3項目を返す。"""
    items = [
        ("平日の睡眠時間", 5.0 - float(result["weekday_score"]), "就寝を15〜30分早める"),
        ("睡眠リズム", min(float(result["sleep_debt"]), 4.0), "休日の起床時刻差を2時間以内にする"),
        ("就寝前スマホ", 5.0 - float(result["phone_control"]), "寝る30分前にスマホを離す"),
        ("スクリーンタイム", 5.0 - float(result["screen_balance"]), "夜の画面時間を昼間へ移す"),
        ("疲労回復", 5.0 - float(result["fatigue_recovery"]), "寝る前の負担を減らす"),
        ("睡眠満足度", 5.0 - float(result["satisfaction"]), "満足できなかった日の要因を記録する"),
        ("睡眠先延ばし", 5.0 - float(result["bedtime_control"]), "行動の終了時刻を決める"),
        ("睡眠優先度", 5.0 - float(result["priority"]), "睡眠時間を予定表に入れる"),
    ]

    items.sort(key=lambda item: item[1], reverse=True)
    return items[:3]


def render_priority_actions(result: dict) -> None:
    """改善優先順位と、今日からできる行動を表示する。"""
    priority_items = build_priority_items(result)

    st.subheader("⭐ 改善優先順位")
    for rank, (label, severity, action) in enumerate(priority_items, start=1):
        stars = max(1, min(5, round(severity)))
        star_text = "★" * stars + "☆" * (5 - stars)

        st.markdown(
            (
                '<div class="advice-card">'
                f'<strong>{rank}．{label}</strong>'
                f'<div style="margin-top:0.3rem;">{star_text}</div>'
                f'<div style="margin-top:0.4rem;">今日の行動：{action}</div>'
                '</div>'
            ),
            unsafe_allow_html=True,
        )

    st.subheader("🌙 今日からできる3つ")
    for index, (_, _, action) in enumerate(priority_items, start=1):
        st.markdown(
            f'<div class="insight-card"><strong>{index}</strong>　{action}</div>',
            unsafe_allow_html=True,
        )


def improvement_message(want_score: int, can_score: int) -> str:
    gap = want_score - can_score

    if gap >= 2:
        return "改善したい気持ちは強い一方、実行が難しい状態です。目標を小さくし、環境や周囲の支援を活用しましょう。"
    if want_score >= 4 and can_score >= 4:
        return "改善意欲と実行可能性の両方が高い状態です。今日から実行する行動を1つ決めましょう。"
    if want_score <= 2:
        return "改善意欲は高くない状態です。まずは睡眠不足が翌日に与える影響を記録してみましょう。"

    return "改善意欲と実行可能性に大きな差はありません。続けやすい行動を1つ選びましょう。"




# ==================================================
# 154名の分析データ平均との差
# ==================================================
def comparison_label(
    user_value: float,
    mean_value: float,
    *,
    tolerance: float = 0.25,
) -> tuple[str, str]:
    """平均との差を3段階で返す。各項目は高いほど良好な向きに統一済み。"""
    difference = user_value - mean_value

    if abs(difference) <= tolerance:
        return "平均との差は小さい", "分析対象者の平均とおおむね同程度です。"
    if difference > 0:
        return "平均より良好", "分析対象者の平均と比べて、良好な傾向です。"
    return "見直し候補", "分析対象者の平均と比べて、見直せる可能性があります。"


def render_mean_comparison(result: dict) -> None:
    """詳細診断の回答を154名の分析データ平均との差で表示する。"""
    rhythm_stability = max(1.0, min(5.0, 5.0 - result["sleep_debt"]))
    mean_rhythm_stability = max(
        1.0,
        min(5.0, 5.0 - float(APPROX_MEANS[1])),
    )

    comparison_items = [
        ("睡眠時間", float(result["weekday_score"]), float(APPROX_MEANS[0])),
        ("リズム安定", rhythm_stability, mean_rhythm_stability),
        ("就寝前スマホ", float(result["phone_control"]), float(APPROX_MEANS[2])),
        ("画面時間", float(result["screen_balance"]), float(APPROX_MEANS[3])),
        ("疲労回復", float(result["fatigue_recovery"]), float(APPROX_MEANS[4])),
        ("睡眠満足度", float(result["satisfaction"]), float(APPROX_MEANS[5])),
        ("就寝管理", float(result["bedtime_control"]), float(APPROX_MEANS[7])),
        ("睡眠優先度", float(result["priority"]), float(APPROX_MEANS[8])),
    ]

    st.subheader("👥 154名の分析データ平均との差")
    st.caption(
        "各項目は5点満点です。平均値は研究時の標準化情報から復元した近似値です。"
    )

    for label, user_value, mean_value in comparison_items:
        status, description = comparison_label(user_value, mean_value)
        difference = user_value - mean_value

        st.markdown(
            (
                '<div class="insight-card">'
                '<div style="display:flex;justify-content:space-between;gap:1rem;">'
                f'<strong>{label}</strong><strong>{status}</strong>'
                '</div>'
                '<div style="margin-top:0.35rem;">'
                f'あなた：{user_value:.1f}点 ／ 全体平均：約{mean_value:.1f}点 '
                f'（差 {difference:+.1f}点）'
                '</div>'
                '<div style="margin-top:0.25rem;opacity:0.82;">'
                f'{description}'
                '</div>'
                '</div>'
            ),
            unsafe_allow_html=True,
        )

        user_col, mean_col = st.columns(2)
        with user_col:
            st.progress(
                max(0.0, min(1.0, user_value / 5.0)),
                text=f"あなた　{user_value:.1f} / 5",
            )
        with mean_col:
            st.progress(
                max(0.0, min(1.0, mean_value / 5.0)),
                text=f"全体平均　約{mean_value:.1f} / 5",
            )



# ==================================================
# 個別総評
# ==================================================
def build_personal_summary(result: dict) -> str:
    """回答パターンから、優先して見直したいポイントを文章化する。"""
    candidates = [
        (
            5.0 - float(result["weekday_score"]),
            "平日の睡眠時間",
            "まずは就寝時刻を15〜30分早めることから始めると取り組みやすいです。",
        ),
        (
            min(float(result["sleep_debt"]), 4.0),
            "平日と休日の睡眠時間差",
            "休日の起床時刻を平日との差2時間以内に近づけることがポイントです。",
        ),
        (
            5.0 - float(result["phone_control"]),
            "就寝前のスマートフォン利用",
            "寝る30分前からスマートフォンを手の届かない場所に置く方法がおすすめです。",
        ),
        (
            5.0 - float(result["screen_balance"]),
            "1日のスクリーンタイム",
            "夜に集中している画面時間を、昼間や移動時間へ分散してみましょう。",
        ),
        (
            5.0 - float(result["fatigue_recovery"]),
            "起床時の疲労感",
            "睡眠時間だけでなく、寝る前の過ごし方や日中の負担も振り返る必要があります。",
        ),
        (
            5.0 - float(result["satisfaction"]),
            "睡眠満足度",
            "満足できなかった日の行動を記録すると、改善すべき原因を見つけやすくなります。",
        ),
        (
            5.0 - float(result["bedtime_control"]),
            "睡眠の先延ばし",
            "就寝時刻を決めるだけでなく、終了時刻を決めて行動を切り上げる工夫が有効です。",
        ),
        (
            5.0 - float(result["priority"]),
            "睡眠の優先度",
            "睡眠を予定表に入れ、他の予定と同じように確保することが改善の第一歩です。",
        ),
    ]

    candidates.sort(key=lambda item: item[0], reverse=True)
    first = candidates[0]
    second = candidates[1]

    if first[0] <= 1.0:
        return (
            "睡眠の量・質・生活習慣は全体として比較的安定しています。"
            "現在できている習慣を維持し、変化があったときに早めに調整しましょう。"
        )

    return (
        f"今回の回答では、特に「{first[1]}」が優先的な見直しポイントです。"
        f"{first[2]} また、「{second[1]}」にも注意すると、"
        "睡眠全体のバランスを整えやすくなります。"
    )


def render_personal_summary(result: dict) -> None:
    """診断結果に個別総評を表示する。"""
    st.subheader("📝 あなたへの総評")
    summary = build_personal_summary(result)
    st.markdown(
        f'<div class="description-card">{summary}</div>',
        unsafe_allow_html=True,
    )


# ==================================================
# URLベースの画面管理
# ==================================================
VALID_PAGES = {
    "home",
    "simple",
    "simple_result",
    "detail",
    "detail_result",
    "about",
}

if "simple_result" not in st.session_state:
    st.session_state.simple_result = None

if "detail_result" not in st.session_state:
    st.session_state.detail_result = None


def current_page() -> str:
    page = st.query_params.get("page", "home")
    if isinstance(page, list):
        page = page[0] if page else "home"
    return page if page in VALID_PAGES else "home"


def go_to(page_name: str) -> None:
    """URLのpageパラメータを変更して画面を切り替える。"""
    if page_name not in VALID_PAGES:
        page_name = "home"

    st.query_params["page"] = page_name
    st.rerun()


def scroll_to_top() -> None:
    """画面切り替え後に表示位置を上へ戻す。"""
    components.html(
        """
        <script>
            const scrollTop = () => {
                const doc = window.parent.document;
                const main =
                    doc.querySelector('[data-testid="stAppViewContainer"]') ||
                    doc.querySelector('section.main');

                if (main) {
                    main.scrollTo({top: 0, left: 0, behavior: "auto"});
                    main.scrollTop = 0;
                }

                window.parent.scrollTo(0, 0);
                doc.documentElement.scrollTop = 0;
                doc.body.scrollTop = 0;
            };

            scrollTop();
            setTimeout(scrollTop, 100);
            setTimeout(scrollTop, 350);
        </script>
        """,
        height=0,
    )


def show_type_image(info: dict, width: int = 280) -> None:
    """画像をBase64でHTMLに直接埋め込み、ブラウザ依存の表示不具合を避ける。"""
    import base64
    import html

    image_path = Path(__file__).resolve().parent / info["image"]

    if not image_path.is_file():
        st.error(f"画像が見つかりません: {image_path}")
        return

    try:
        image_bytes = image_path.read_bytes()
        encoded_image = base64.b64encode(image_bytes).decode("ascii")
        safe_alt = html.escape(info.get("name", "睡眠タイプ画像"))

        st.markdown(
            (
                '<div style="margin:0.5rem 0 1rem;">'
                f'<img src="data:image/png;base64,{encoded_image}" '
                f'alt="{safe_alt}" '
                f'style="width:{width}px; max-width:100%; height:auto; '
                'border-radius:14px; display:inline-block;">'
                '</div>'
            ),
            unsafe_allow_html=True,
        )
    except Exception as error:
        st.error(
            f"画像を表示できませんでした："
            f"{image_path.name}（{type(error).__name__}: {error}）"
        )

# ==================================================
# ホーム画面
# ==================================================
def show_home() -> None:
    scroll_to_top()

    st.markdown(
        """
        <div class="hero-card">
            <p class="hero-title">🌙 Sleep Compass</p>
            <p class="hero-subtitle">
                あなたに合った睡眠改善への道しるべ。<br>
                154名の研究データをもとに、睡眠タイプと改善の優先順位を可視化します。
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "このアプリは生活習慣を振り返るための試作版であり、"
        "医療上の診断を行うものではありません。"
    )

    st.subheader("診断メニュー")

    if st.button("🐧 簡易診断", width="stretch"):
        go_to("simple")

    if st.button("📊 詳細診断", width="stretch"):
        go_to("detail")

    if st.button("ℹ️ このアプリについて", width="stretch"):
        go_to("about")


# ==================================================
# 簡易診断
# ==================================================
def show_simple_diagnosis() -> None:
    scroll_to_top()

    st.title("🐧 かんたん睡眠タイプ診断")
    st.write("当てはまる項目にチェックしてください。")

    with st.form("simple_diagnosis_form"):
        show_type_image(TYPE_INFO[0], width=180)
        st.subheader("① 高疲労型")
        hf1 = st.checkbox("起床時に疲れが残っている")
        hf2 = st.checkbox("現在の睡眠に満足していない")
        hf3 = st.checkbox("睡眠時間をもっと長くしたい")
        hf4 = st.checkbox("ストレスや不安で眠れないことがある")

        st.divider()
        show_type_image(TYPE_INFO[1], width=180)
        st.subheader("② 規則的生活型")
        rg1 = st.checkbox("生活リズムは比較的安定している")
        rg2 = st.checkbox("睡眠に大きな悩みはない")
        rg3 = st.checkbox("仕事・家事など外的要因で睡眠不足になる")
        rg4 = st.checkbox("睡眠は改善したいが、大きな問題ではない")

        st.divider()
        show_type_image(TYPE_INFO[2], width=180)
        st.subheader("③ 良好睡眠型")
        gd1 = st.checkbox("起床時に疲れが残っていない")
        gd2 = st.checkbox("現在の睡眠に満足している")
        gd3 = st.checkbox("平日も十分な睡眠が取れている")
        gd4 = st.checkbox("睡眠習慣が安定している")

        st.divider()
        show_type_image(TYPE_INFO[3], width=180)
        st.subheader("④ 睡眠負債型")
        db1 = st.checkbox("平日の睡眠時間が6時間未満の日が多い")
        db2 = st.checkbox("休日は平日より2時間以上長く眠る")
        db3 = st.checkbox("睡眠よりも、やりたいことを優先する")
        db4 = st.checkbox("夜更かしが習慣化している")

        submitted = st.form_submit_button(
            "🧭 診断結果を見る",
            width="stretch",
        )

    if submitted:
        scores = {
            "高疲労型": sum([hf1, hf2, hf3, hf4]),
            "規則的生活型": sum([rg1, rg2, rg3, rg4]),
            "良好睡眠型": sum([gd1, gd2, gd3, gd4]),
            "睡眠負債型": sum([db1, db2, db3, db4]),
        }

        matched_types = [
            name for name, score in scores.items() if score >= 2
        ]
        candidates = matched_types if matched_types else list(scores)

        main_name = max(
            candidates,
            key=lambda name: (scores[name], SIMPLE_PRIORITY[name]),
        )

        st.session_state.simple_result = {
            "main_name": main_name,
            "sub_names": [
                name for name in matched_types if name != main_name
            ],
            "scores": scores,
            "clear_match": bool(matched_types),
        }

        go_to("simple_result")

    if st.button("← ホームへ戻る"):
        go_to("home")


# ==================================================
# 簡易結果
# ==================================================
def show_simple_result() -> None:
    scroll_to_top()

    result = st.session_state.simple_result
    if result is None:
        st.warning("簡易診断の回答がありません。")
        if st.button("簡易診断へ進む", width="stretch"):
            go_to("simple")
        return

    main_name = result["main_name"]
    type_id = NAME_TO_ID[main_name]
    info = TYPE_INFO[type_id]

    show_type_image(info)

    st.markdown(
        f"""
        <div class="result-card">
            <div style="font-size:3.6rem;">{info["icon"]}</div>
            <div style="font-size:0.95rem; opacity:0.85;">
                あなたの主な睡眠タイプ
            </div>
            <div style="font-size:1.9rem; font-weight:800; margin-top:0.5rem;">
                {main_name}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if result["clear_match"]:
        st.write(
            f"4項目中 **{result['scores'][main_name]}項目** が当てはまりました。"
        )
    else:
        st.warning(
            "2項目以上当てはまるタイプがなかったため、"
            "最も点数が高いタイプを参考結果として表示しています。"
        )

    st.markdown(
        f'<div class="description-card">{info["description"]}</div>',
        unsafe_allow_html=True,
    )

    if result["sub_names"]:
        st.info(
            "次のタイプの特徴もみられます："
            + "、".join(result["sub_names"])
        )

    st.subheader("📊 タイプ別チェック結果")
    for name, score in result["scores"].items():
        st.progress(score / 4, text=f"{name}：4項目中{score}項目")

    st.subheader("💡 最初に取り組みたいこと")
    for advice in info["advice"]:
        st.markdown(
            f'<div class="advice-card">✅ {advice}</div>',
            unsafe_allow_html=True,
        )

    st.write(
        f"有効回答154名のうち、"
        f"**{info['count']}名（{info['percentage']:.1f}%）**が"
        f"「{main_name}」に分類されました。"
    )

    if st.button("📊 9項目で詳しく分析する", width="stretch"):
        go_to("detail")

    if st.button("もう一度簡易診断する", width="stretch"):
        go_to("simple")

    if st.button("← ホームへ戻る"):
        go_to("home")


# ==================================================
# 詳細診断
# ==================================================
def show_detail_diagnosis() -> None:
    scroll_to_top()

    st.title("📊 9項目の詳細診断")
    st.write("研究で使用した9変数から、睡眠タイプを詳しく分析します。")

    with st.form("detail_diagnosis_form"):
        name = st.text_input("名前またはニックネーム")

        st.subheader("1．睡眠の量")
        weekday_sleep = st.selectbox(
            "平日の平均睡眠時間",
            SLEEP_OPTIONS,
            index=2,
        )
        holiday_sleep = st.selectbox(
            "休日の平均睡眠時間",
            SLEEP_OPTIONS,
            index=3,
        )

        st.subheader("2．睡眠の質")
        fatigue_option = st.radio(
            "起床時に疲労感がありますか？",
            FATIGUE_OPTIONS,
            index=2,
        )
        satisfaction_option = st.radio(
            "現在の睡眠に満足していますか？",
            SATISFACTION_OPTIONS,
            index=2,
        )

        st.subheader("3．デジタル行動")
        phone_option = st.radio(
            "就寝前1時間以内に、スマートフォンを5分以上使用しますか？",
            PHONE_OPTIONS,
            index=2,
        )
        screen_option = st.radio(
            "1日の平均スクリーンタイム",
            SCREEN_OPTIONS,
            index=2,
        )

        st.subheader("4．生活リズムと睡眠への意識")
        chronotype_option = st.radio(
            "あなたは朝型・夜型のどちらに近いですか？",
            CHRONOTYPE_OPTIONS,
            index=2,
        )
        postpone_option = st.radio(
            "睡眠よりも目先の楽しさを優先してしまいますか？",
            POSTPONE_OPTIONS,
            index=2,
        )
        priority_option = st.radio(
            "あなたにとって、睡眠の優先度はどの程度ですか？",
            PRIORITY_OPTIONS,
            index=2,
        )

        st.subheader("5．改善への気持ち")
        st.caption(
            "次の2問はタイプ判定ではなく、改善提案の個別化に使用します。"
        )
        want_option = st.radio(
            "睡眠時間を長くしたいと思いますか？",
            WANT_OPTIONS,
            index=2,
        )
        can_option = st.radio(
            "現実的に睡眠時間を増やせそうですか？",
            CAN_OPTIONS,
            index=2,
        )

        submitted = st.form_submit_button(
            "🧭 詳細結果を見る",
            width="stretch",
        )

    if submitted:
        weekday_score = SLEEP_SCORE_MAP[weekday_sleep]
        weekday_hours = SLEEP_HOURS_MAP[weekday_sleep]
        holiday_hours = SLEEP_HOURS_MAP[holiday_sleep]
        sleep_debt = max(holiday_hours - weekday_hours, 0)

        phone_control = PHONE_SCORE_MAP[phone_option]
        screen_balance = SCREEN_SCORE_MAP[screen_option]
        fatigue_recovery = FATIGUE_SCORE_MAP[fatigue_option]
        satisfaction = SATISFACTION_SCORE_MAP[satisfaction_option]
        chronotype = CHRONOTYPE_SCORE_MAP[chronotype_option]
        bedtime_control = POSTPONE_SCORE_MAP[postpone_option]
        priority = PRIORITY_SCORE_MAP[priority_option]

        user_values = [
            weekday_score,
            sleep_debt,
            phone_control,
            screen_balance,
            fatigue_recovery,
            satisfaction,
            chronotype,
            bedtime_control,
            priority,
        ]

        with st.spinner("研究データと照合しています…"):
            time.sleep(0.5)
            type_id = diagnose_detail(user_values)

        insights = []
        if weekday_hours < 6:
            insights.append("平日の睡眠時間が6時間未満です。")
        if sleep_debt >= 2:
            insights.append(
                f"休日は平日より約{sleep_debt:.1f}時間長く眠っています。"
            )
        if phone_control <= 2:
            insights.append("就寝前のスマートフォン利用が習慣化しています。")
        if fatigue_recovery <= 2:
            insights.append("起床時に疲労が残りやすい状態です。")
        if satisfaction <= 2:
            insights.append("睡眠満足度が低い傾向です。")
        if bedtime_control <= 2:
            insights.append("睡眠を先延ばししやすい傾向です。")
        if priority <= 2:
            insights.append("睡眠の優先度が低くなりやすい傾向です。")
        if not insights:
            insights.append(
                "睡眠の量・質・生活習慣に大きな偏りはみられません。"
            )

        st.session_state.detail_result = {
            "name": name.strip(),
            "type_id": type_id,
            "weekday_sleep": weekday_sleep,
            "holiday_sleep": holiday_sleep,
            "weekday_score": weekday_score,
            "sleep_debt": sleep_debt,
            "phone_control": phone_control,
            "screen_balance": screen_balance,
            "fatigue_recovery": fatigue_recovery,
            "satisfaction": satisfaction,
            "bedtime_control": bedtime_control,
            "priority": priority,
            "insights": insights,
            "improvement": improvement_message(
                WANT_SCORE_MAP[want_option],
                CAN_SCORE_MAP[can_option],
            ),
        }

        go_to("detail_result")

    if st.button("← ホームへ戻る"):
        go_to("home")


# ==================================================
# 詳細結果
# ==================================================
def calculate_sleep_score(result: dict) -> int:
    """詳細診断の回答から100点満点のSleep Scoreを計算する。"""

    score = 0

    # 平日の睡眠時間：20点
    weekday_score = result.get("weekday_score", 3)
    weekday_points = {
        1: 4,
        2: 10,
        3: 16,
        4: 20,
        5: 17,
    }
    score += weekday_points.get(weekday_score, 0)

    # 睡眠負債：15点
    sleep_debt = result.get("sleep_debt", 0)
    if sleep_debt <= 0.5:
        score += 15
    elif sleep_debt <= 1.0:
        score += 12
    elif sleep_debt <= 2.0:
        score += 7
    else:
        score += 2

    # 就寝前スマホ
    score += result.get("phone_control", 3) * 2

    # スクリーンタイム
    score += result.get("screen_balance", 3) * 2

    # 疲労回復感
    score += result.get("fatigue_recovery", 3) * 3

    # 睡眠満足度
    score += result.get("satisfaction", 3) * 3

    # 就寝時刻の自己管理
    score += result.get("bedtime_control", 3)

    # 睡眠優先度
    score += result.get("priority", 3)

    return max(0, min(100, round(score)))

def show_detail_result() -> None:
    scroll_to_top()

    result = st.session_state.detail_result
    if result is None:
        st.warning("詳細診断の回答がありません。")
        if st.button("詳細診断へ進む", width="stretch"):
            go_to("detail")
        return

    info = TYPE_INFO[result["type_id"]]
    result_label = (
        f"{result['name']}さんの睡眠タイプ"
        if result["name"]
        else "あなたの睡眠タイプ"
    )
    sleep_score = calculate_sleep_score(result)

    if sleep_score >= 80:
        score_message = "とても良好な睡眠習慣です。"
        score_level = "Excellent"
    elif sleep_score >= 65:
        score_message = "比較的良好ですが、改善できる点もあります。"
        score_level = "Good"
    elif sleep_score >= 50:
        score_message = "睡眠習慣にいくつか見直しポイントがあります。"
        score_level = "Fair"
    else:
        score_message = "睡眠不足や生活習慣を見直してみましょう。"
        score_level = "Needs attention"

    score_html = f"""<div style="background: linear-gradient(135deg, #eef3ff 0%, #dce6ff 100%); padding: 24px; border-radius: 20px; text-align: center; margin: 12px 0 24px 0; box-shadow: 0 4px 12px rgba(30, 50, 110, 0.10);">
<div style="font-size: 18px; font-weight: 700; color: #263a7a;">🌙 Sleep Score</div>
<div style="font-size: 52px; font-weight: 800; color: #3d56a6; line-height: 1.2; margin-top: 4px;">{sleep_score}<span style="font-size: 24px; color: #6171a8;"> / 100</span></div>
<div style="font-weight: 700; color: #263a7a; margin-top: 6px;">{score_level}</div>\n<div style="font-size: 15px; color: #334155; margin-top: 8px;">{score_message}</div>
<div style="background: #ffffff; border-radius: 999px; height: 12px; margin: 18px auto 0 auto; max-width: 420px; overflow: hidden;">
<div style="width: {sleep_score}%; height: 100%; background: linear-gradient(90deg, #4257a6, #7185d2); border-radius: 999px;"></div>
</div>
</div>"""
    st.markdown(score_html, unsafe_allow_html=True)

    show_type_image(info)

    st.markdown(
            f"""
            <div class="result-card">
                <div style="font-size:3.6rem;">{info["icon"]}</div>
                <div style="font-size:0.95rem; opacity:0.85;">
                    {result_label}
                </div>
                <div style="font-size:1.9rem; font-weight:800; margin-top:0.5rem;">
                    {info["name"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
            f'<div class="description-card">{info["description"]}</div>',
            unsafe_allow_html=True,
        )

    sleep_debt_display = (
        f"+{result['sleep_debt']:.1f}時間"
        if result["sleep_debt"] > 0
        else "0時間"
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "🌙 平日",
            SLEEP_DISPLAY_MAP[result["weekday_sleep"]],
        )
    with col2:
        st.metric(
            "🌞 休日",
            SLEEP_DISPLAY_MAP[result["holiday_sleep"]],
        )
    with col3:
        st.metric("📈 睡眠負債", sleep_debt_display)

    st.subheader("📊 あなたの睡眠バランス")
    radar = create_comparison_radar_chart(result)
    st.plotly_chart(
        radar,
        width="stretch",
        config={"displayModeBar": False},
    )

    render_mean_comparison(result)

    render_personal_summary(result)

    render_priority_actions(result)

    st.subheader("🔍 回答から分かったこと")
    for insight in result["insights"]:
        st.markdown(
            f'<div class="insight-card">・{insight}</div>',
            unsafe_allow_html=True,
        )

    st.subheader("🧭 改善意欲と実行可能性")
    st.markdown(
        f'<div class="description-card">{result["improvement"]}</div>',
        unsafe_allow_html=True,
    )

    st.subheader("💡 タイプ別改善ポイント")
    for advice in info["advice"]:
        st.markdown(
            f'<div class="advice-card">✅ {advice}</div>',
            unsafe_allow_html=True,
        )

    st.write(
        f"有効回答154名のうち、"
        f"**{info['count']}名（{info['percentage']:.1f}%）**が"
        f"「{info['name']}」に分類されました。"
    )

    st.caption(
        "Sleep Scoreは回答項目を独自に重み付けした参考指標です。"
        "睡眠タイプは9項目の組み合わせから判定するため、"
        "同じスコアでも異なるタイプになることがあります。"
    )

    if st.button("もう一度詳細診断する", width="stretch"):
        go_to("detail")

    if st.button("← ホームへ戻る"):
        go_to("home")


# ==================================================
# About
# ==================================================
def show_about() -> None:
    scroll_to_top()

    st.title("ℹ️ Sleep Compassについて")

    st.markdown(
        """
        ### 開発背景

        同じ睡眠不足でも、疲労、生活環境、デジタル行動、
        睡眠への意識など、その背景は一様ではありません。

        Sleep Compassは、一律の助言ではなく、
        睡眠タイプに応じた改善提案を届けることを目的に作成しました。

        ### 分析概要

        - 回収回答：168件
        - 有効回答：154件
        - 使用変数：睡眠に関連する9変数
        - 分析手法：標準化、K-meansクラスタリング
        - クラスタ数：4
        - 妥当性確認：Kruskal-Wallis検定

        ### 使用技術

        - Python
        - Streamlit
        - NumPy
        - Plotly
        - K-means clustering
        - ルールベース分類
        - 個別フィードバック生成
        - 比較レーダーチャート
        - 改善優先順位の可視化

        ### 注意事項

        本アプリは生活習慣を振り返るための試作版です。
        医療上の診断や治療を目的とするものではありません。
        """
    )

    if st.button("← ホームへ戻る"):
        go_to("home")


# ==================================================
# 画面切り替え
# ==================================================
page = current_page()

if page == "home":
    show_home()
elif page == "simple":
    show_simple_diagnosis()
elif page == "simple_result":
    show_simple_result()
elif page == "detail":
    show_detail_diagnosis()
elif page == "detail_result":
    show_detail_result()
elif page == "about":
    show_about()
   
