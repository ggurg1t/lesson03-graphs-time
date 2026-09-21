import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"
)

# 그래프마다 '이 그래프로 알 수 있는 것' 한 문장을 여기에 적으면 그래프 아래에 표시돼요.
# 비워 두면 안내 문구가 대신 보여요.
INSIGHTS = {
    "graph_01": "",
    "graph_02": "",
    "graph_03": "",
    "graph_04": "",
    "graph_05": "",
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


def section_02_top5_compare(df: pd.DataFrame) -> None:
    st.header("그래프 2. 일관객 합계 상위 5편 비교")

    # 이 기간 일관객 합계가 가장 큰 5편 (큰 순서)
    top5 = (
        df.groupby("영화명")["일관객"].sum().sort_values(ascending=False).head(5).index.tolist()
    )
    top5_df = df[df["영화명"].isin(top5)]

    fig = px.line(
        top5_df,
        x="날짜",
        y="일관객",
        color="영화명",
        category_orders={"영화명": top5},  # 범례를 합계 큰 순서로
        markers=True,
        title="일관객 합계 상위 5편 — 날짜별 일관객",
    )
    fig.update_traces(
        hovertemplate="%{x|%Y-%m-%d}<br>일관객 %{y:,}명<extra>%{fullData.name}</extra>"
    )
    fig.update_layout(
        xaxis_title="날짜",
        yaxis_title="일관객(명)",
        legend_title_text="영화 (클릭: 켜기/끄기)",
        hovermode="closest",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.caption("범례의 영화 이름을 한 번 누르면 그 영화가 꺼지고, 더블클릭하면 그 영화만 남아요.")
    show_insight("graph_02")


def section_03_daily_total(df: pd.DataFrame) -> None:
    st.header("그래프 3. 날짜별 10위권 일관객 합계")

    # 날짜별로 그날 10위권 일관객을 모두 더함
    daily = df.groupby("날짜", as_index=False)["일관객"].sum()
    daily = daily.rename(columns={"일관객": "일관객합계"})

    # 합계가 가장 컸던 3일
    top3 = daily.nlargest(3, "일관객합계").sort_values("일관객합계", ascending=False)

    fig = px.area(daily, x="날짜", y="일관객합계", title="날짜별 10위권 일관객 합계")
    fig.update_traces(
        hovertemplate="%{x|%Y-%m-%d}<br>합계 %{y:,}명<extra></extra>"
    )

    # 최고 3일: 점 + 날짜 글자 (가까운 날짜끼리 글자가 겹치지 않게 위치를 다르게)
    fig.add_trace(
        go.Scatter(
            x=top3["날짜"],
            y=top3["일관객합계"],
            mode="markers+text",
            marker=dict(color="crimson", size=11, line=dict(color="white", width=1.5)),
            text=top3["날짜"].dt.strftime("%Y-%m-%d"),
            textposition=["top center", "top right", "top left"][: len(top3)],
            textfont=dict(color="crimson", size=13),
            hovertemplate="%{x|%Y-%m-%d}<br>합계 %{y:,}명<extra>최고 3일</extra>",
            showlegend=False,
        )
    )

    fig.update_layout(xaxis_title="날짜", yaxis_title="일관객 합계(명)")
    # 위쪽 글자가 잘리지 않게 여유 공간
    fig.update_yaxes(range=[0, daily["일관객합계"].max() * 1.15])
    st.plotly_chart(fig, use_container_width=True)

    show_insight("graph_03")


def section_04_top10_total(df: pd.DataFrame) -> None:
    st.header("그래프 4. 영화별 일관객 합계 TOP 10")

    # 영화별로 일관객 합계와 10위권에 든 날수를 함께 계산
    summary = (
        df.groupby("영화명")
        .agg(총관객=("일관객", "sum"), 순위권일수=("날짜", "nunique"))
        .reset_index()
        .nlargest(10, "총관객")
        .sort_values("총관객", ascending=False)
    )

    fig = px.bar(
        summary,
        x="총관객",
        y="영화명",
        orientation="h",
        custom_data=["순위권일수"],
        title="영화별 일관객 합계 TOP 10",
    )
    fig.update_traces(
        hovertemplate=(
            "%{y}<br>일관객 합계 %{x:,}명"
            "<br>10위권에 든 날 %{customdata[0]}일<extra></extra>"
        )
    )
    # 관객이 많은 영화가 위에 오도록 y축 순서를 뒤집기
    fig.update_yaxes(autorange="reversed", title_text="")
    fig.update_xaxes(title_text="일관객 합계(명)")
    st.plotly_chart(fig, use_container_width=True)

    show_insight("graph_04")


def section_05_month_weekday_heatmap(df: pd.DataFrame) -> None:
    st.header("그래프 5. 월×요일별 일관객 합계")

    weekday_names = ["월", "화", "수", "목", "금", "토", "일"]  # dayofweek: 월=0 … 일=6

    # 날짜에서 월과 요일을 뽑아 월×요일별 일관객 합계 표(피벗)를 만듦
    temp = df.assign(월=df["날짜"].dt.month, 요일=df["날짜"].dt.dayofweek)
    pivot = temp.pivot_table(
        index="월", columns="요일", values="일관객", aggfunc="sum", fill_value=0
    )
    pivot = pivot.reindex(columns=range(7), fill_value=0)  # 월요일 → 일요일 순서
    pivot.columns = [f"{name}요일" for name in weekday_names]
    pivot.index = [f"{m}월" for m in pivot.index]

    fig = px.imshow(
        pivot,
        color_continuous_scale="Blues",  # 진할수록 관객이 많음
        aspect="auto",
        labels=dict(x="요일", y="월", color="일관객 합계(명)"),
        title="월×요일별 일관객 합계",
    )
    fig.update_traces(
        hovertemplate="%{y} %{x}<br>일관객 합계 %{z:,}명<extra></extra>"
    )
    st.plotly_chart(fig, use_container_width=True)

    show_insight("graph_05")


def main() -> None:
    st.title("영화 데이터 그래프 도감 1 - 시간")
    st.caption("KOBIS 일별 박스오피스 10위권 · 1년치(365일)")

    df = load_data()

    section_01_daily_audience(df)
    st.divider()

    section_02_top5_compare(df)
    st.divider()

    section_03_daily_total(df)
    st.divider()

    section_04_top10_total(df)
    st.divider()

    section_05_month_weekday_heatmap(df)
    st.divider()

    # 다음 그래프는 여기에 이어서 추가하세요.
    # section_06_...(df)
    # st.divider()


main()
