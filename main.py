import pandas as pd
import plotly.express as px
import streamlit as st

DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"
)

# 그래프마다 '이 그래프로 알 수 있는 것' 한 문장을 여기에 적으면 그래프 아래에 표시돼요.
# 비워 두면 안내 문구가 대신 보여요.
INSIGHTS = {
    "graph_01": "",
}

st.set_page_config(page_title="영화 데이터 그래프 도감 1 - 시간", layout="wide")


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_URL, dtype={"날짜": str})
    df["날짜"] = pd.to_datetime(df["날짜"], format="%Y%m%d")
    return df.sort_values("날짜").reset_index(drop=True)


def show_insight(key: str) -> None:
    """그래프 아래 '이 그래프로 알 수 있는 것' 문구 자리."""
    text = INSIGHTS.get(key, "").strip()
    if text:
        st.info(f"**이 그래프로 알 수 있는 것** · {text}")
    else:
        st.info("**이 그래프로 알 수 있는 것** · (여기에 한 문장을 적어 주세요)")


# ─────────────────────────────────────────────
# 그래프 구역들 (새 그래프는 함수를 하나 더 만들어 아래 main()에 추가)
# ─────────────────────────────────────────────
def section_01_daily_audience(df: pd.DataFrame) -> None:
    st.header("그래프 1. 영화별 일관객 변화")

    # 관객이 많았던 영화가 위로 오도록 정렬
    movies = (
        df.groupby("영화명")["일관객"].sum().sort_values(ascending=False).index.tolist()
    )
    movie = st.selectbox("영화를 골라 보세요", movies, key="graph_01_movie")

    movie_df = df[df["영화명"] == movie]

    fig = px.line(
        movie_df,
        x="날짜",
        y="일관객",
        markers=True,
        title=f"{movie} — 날짜별 일관객",
    )
    fig.update_traces(
        hovertemplate="%{x|%Y-%m-%d}<br>일관객 %{y:,}명<extra></extra>"
    )
    fig.update_layout(
        xaxis_title="날짜",
        yaxis_title="일관객(명)",
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    show_insight("graph_01")


def main() -> None:
    st.title("영화 데이터 그래프 도감 1 - 시간")
    st.caption("KOBIS 일별 박스오피스 10위권 · 1년치(365일)")

    df = load_data()

    section_01_daily_audience(df)
    st.divider()

    # 다음 그래프는 여기에 이어서 추가하세요.
    # section_02_...(df)
    # st.divider()


main()
