import streamlit as st
import pandas as pd
import plotly.express as px

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/stroke.csv"

st.set_page_config(
    page_title="탐색 | 뇌졸중 예측 실습실",
    page_icon="🔎",
    layout="wide"
)


@st.cache_data
def load_data():
    return pd.read_csv(DATA_URL, encoding="utf-8")


df = load_data()

st.title("🔎 탐색")
st.caption("뇌졸중 데이터의 분포와 변수 사이의 차이를 그래프로 살펴봅니다.")

st.markdown("---")


# --------------------------------------------------
# 1. 나이와 평균 혈당의 분포
# --------------------------------------------------
st.header("1. 나이와 평균 혈당의 분포")

col1, col2 = st.columns(2)

with col1:
    fig_age = px.histogram(
        df,
        x="age",
        nbins=30,
        title="나이 분포",
        labels={
            "age": "나이",
            "count": "사람 수"
        }
    )

    fig_age.update_layout(
        xaxis_title="나이",
        yaxis_title="사람 수"
    )

    st.plotly_chart(
        fig_age,
        use_container_width=True
    )


with col2:
    fig_glucose = px.histogram(
        df,
        x="avg_glucose_level",
        nbins=30,
        title="평균 혈당 분포",
        labels={
            "avg_glucose_level": "평균 혈당",
            "count": "사람 수"
        }
    )

    fig_glucose.update_layout(
        xaxis_title="평균 혈당",
        yaxis_title="사람 수"
    )

    st.plotly_chart(
        fig_glucose,
        use_container_width=True
    )


st.markdown("---")


# --------------------------------------------------
# 2. 뇌졸중 여부에 따른 나이와 평균 혈당 비교
# --------------------------------------------------
st.header("2. 뇌졸중 여부에 따른 비교")

box_df = df.copy()

box_df["stroke_group"] = box_df["stroke"].map({
    0: "뇌졸중 없음",
    1: "뇌졸중 있음"
})


col1, col2 = st.columns(2)

with col1:
    fig_age_box = px.box(
        box_df,
        x="stroke_group",
        y="age",
        title="뇌졸중 여부에 따른 나이",
        labels={
            "stroke_group": "뇌졸중 여부",
            "age": "나이"
        }
    )

    st.plotly_chart(
        fig_age_box,
        use_container_width=True
    )


with col2:
    fig_glucose_box = px.box(
        box_df,
        x="stroke_group",
        y="avg_glucose_level",
        title="뇌졸중 여부에 따른 평균 혈당",
        labels={
            "stroke_group": "뇌졸중 여부",
            "avg_glucose_level": "평균 혈당"
        }
    )

    st.plotly_chart(
        fig_glucose_box,
        use_container_width=True
    )


mean_table = (
    box_df
    .groupby("stroke_group")[["age", "avg_glucose_level"]]
    .mean()
    .rename(columns={
        "age": "나이 평균",
        "avg_glucose_level": "평균 혈당 평균"
    })
    .reindex([
        "뇌졸중 없음",
        "뇌졸중 있음"
    ])
    .round(2)
)

st.subheader("두 그룹의 평균값")

st.dataframe(
    mean_table,
    use_container_width=True
)


st.markdown("---")


# --------------------------------------------------
# 3. 고혈압과 심장병에 따른 뇌졸중 비율
# --------------------------------------------------
st.header("3. 고혈압과 심장병에 따른 뇌졸중 비율")


def make_rate_df(column):
    result = (
        df.groupby(column)["stroke"]
        .agg(["mean", "count"])
        .reset_index()
    )

    result["group"] = result[column].map({
        0: "없음",
        1: "있음"
    })

    result["stroke_rate"] = result["mean"] * 100

    return result


hypertension_rate = make_rate_df("hypertension")
heart_rate = make_rate_df("heart_disease")


col1, col2 = st.columns(2)


with col1:
    fig_hyper = px.bar(
        hypertension_rate,
        x="group",
        y="stroke_rate",
        title="고혈압 여부에 따른 뇌졸중 비율",
        labels={
            "group": "고혈압",
            "stroke_rate": "뇌졸중 비율 (%)"
        },
        text="stroke_rate"
    )

    fig_hyper.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )

    st.plotly_chart(
        fig_hyper,
        use_container_width=True
    )


with col2:
    fig_heart = px.bar(
        heart_rate,
        x="group",
        y="stroke_rate",
        title="심장병 여부에 따른 뇌졸중 비율",
        labels={
            "group": "심장병",
            "stroke_rate": "뇌졸중 비율 (%)"
        },
        text="stroke_rate"
    )

    fig_heart.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )

    st.plotly_chart(
        fig_heart,
        use_container_width=True
    )


st.markdown("---")


# --------------------------------------------------
# 4. BMI가 비어 있는 사람의 뇌졸중 비율
# --------------------------------------------------
st.header("4. BMI가 비어 있는 사람의 뇌졸중 비율")

missing_bmi = df[df["bmi"].isna()]

missing_bmi_rate = (
    missing_bmi["stroke"].mean() * 100
)

overall_rate = (
    df["stroke"].mean() * 100
)


bmi_rate_table = pd.DataFrame({
    "구분": [
        "BMI가 비어 있는 사람",
        "전체 사람"
    ],
    "사람 수": [
        len(missing_bmi),
        len(df)
    ],
    "뇌졸중 비율 (%)": [
        missing_bmi_rate,
        overall_rate
    ]
})

bmi_rate_table["뇌졸중 비율 (%)"] = (
    bmi_rate_table["뇌졸중 비율 (%)"]
    .round(2)
)


st.dataframe(
    bmi_rate_table,
    use_container_width=True,
    hide_index=True
)


st.markdown("---")


# --------------------------------------------------
# 5. 흡연 상태별 사람 수
# --------------------------------------------------
st.header("5. 흡연 상태별 사람 수")

smoking_count = (
    df["smoking_status"]
    .value_counts(dropna=False)
    .rename_axis("흡연 상태")
    .reset_index(name="사람 수")
)

smoking_count["흡연 상태"] = (
    smoking_count["흡연 상태"]
    .fillna("빈 값")
)


st.dataframe(
    smoking_count,
    use_container_width=True,
    hide_index=True
)
