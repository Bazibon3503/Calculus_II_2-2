import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# 페이지 및 한글 그래프 설정
# ==========================================
st.set_page_config(
    page_title="배달 도착시간 예측 시뮬레이터",
    page_icon="🛵",
    layout="wide"
)

plt.rcParams["axes.unicode_minus"] = False

# ==========================================
# 1. 수학적 계산 함수
# ==========================================
def speed(t, v0, vmin, k):
    """시간 t에서의 이동 속도 (km/h)"""
    return vmin + (v0 - vmin) * np.exp(-k * t)


def speed_change(t, v0, vmin, k):
    """미분을 이용한 속도 변화율 ((km/h)/분)"""
    return -k * (v0 - vmin) * np.exp(-k * t)


def distance(t, v0, vmin, k):
    """정적분을 이용한 누적 이동 거리 (km)"""
    return (
        vmin * t
        + (v0 - vmin) / k * (1 - np.exp(-k * t))
    ) / 60


def find_arrival_time(v0, vmin, k, D):
    """이분법으로 목적지 도착시간 계산 (분)"""
    low = 0.0
    high = 1.0

    # vmin이 양수이므로 이동 거리는 계속 증가한다.
    while distance(high, v0, vmin, k) < D:
        high *= 2
        if high > 1_000_000:
            raise ValueError("입력값으로 도착시간을 계산할 수 없습니다.")

    for _ in range(100):
        mid = (low + high) / 2
        if distance(mid, v0, vmin, k) < D:
            low = mid
        else:
            high = mid

    return (low + high) / 2


def format_time(total_minutes):
    """분 단위 시간을 시·분·초로 변환"""
    total_seconds = int(round(total_minutes * 60))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours > 0:
        return f"{hours}시간 {minutes}분 {seconds}초"
    return f"{minutes}분 {seconds}초"


# ==========================================
# 2. 화면 제목 및 설명
# ==========================================
st.title("🛵 배달 도착시간 예측 시뮬레이터")
st.subheader("지수함수와 미적분을 활용한 이동 속도 및 도착시간 예측")
st.write(
    "시간에 따른 이동 속도를 지수함수로 모델링하고, "
    "미분과 정적분을 이용하여 속도 변화율과 누적 이동 거리를 계산합니다."
)

st.divider()

# ==========================================
# 3. 사용자 변수 설정
# ==========================================
st.sidebar.header("⚙️ 사용자 변수 설정")
st.sidebar.caption("아래 값을 변경한 후 예측 버튼을 눌러주세요.")

v0 = st.sidebar.number_input(
    "초기 이동 속도 v₀ (km/h)",
    min_value=0.1, value=30.0, step=1.0
)
vmin = st.sidebar.number_input(
    "최저 이동 속도 v_min (km/h)",
    min_value=0.1, value=20.0, step=1.0
)
k = st.sidebar.number_input(
    "속도 변화 상수 k (1/분)",
    min_value=0.001, value=0.08, step=0.01, format="%.3f"
)
D = st.sidebar.number_input(
    "목적지까지 거리 D (km)",
    min_value=0.01, value=5.0, step=0.5
)

if st.sidebar.button("🔄 기본값 복원", use_container_width=True):
    st.rerun()

run_calculation = st.sidebar.button(
    "📊 예측 및 그래프 생성",
    type="primary",
    use_container_width=True
)

# 첫 화면에서도 기본값으로 계산 결과 표시
if "has_calculated" not in st.session_state:
    st.session_state.has_calculated = True

if run_calculation:
    st.session_state.has_calculated = True

# ==========================================
# 4. 계산 및 결과 표시
# ==========================================
if st.session_state.has_calculated:
    try:
        if min(v0, vmin, k, D) <= 0:
            st.error("모든 변수는 0보다 커야 합니다.")
            st.stop()

        arrival = find_arrival_time(v0, vmin, k, D)
        final_speed = speed(arrival, v0, vmin, k)
        initial_rate = speed_change(0, v0, vmin, k)

        st.header("📍 예측 결과")

        col1, col2, col3 = st.columns(3)
        col1.metric("예상 도착시간", format_time(arrival))
        col2.metric("도착 시점 속도", f"{final_speed:.2f} km/h")
        col3.metric("출발 직후 속도 변화율", f"{initial_rate:.4f}")

        st.caption(
            f"목적지 거리: {D:.2f} km  |  "
            f"출발 직후 속도: {v0:.2f} km/h  |  "
            f"최저 이동 속도: {vmin:.2f} km/h"
        )

        st.divider()

        # ==========================================
        # 5. 그래프 생성
        # ==========================================
        st.header("📈 이동 속도 및 누적 이동 거리 그래프")

        end_time = max(30, arrival * 1.2)
        t = np.linspace(0, end_time, 400)
        v = speed(t, v0, vmin, k)
        s = distance(t, v0, vmin, k)

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

        # 속도 그래프
        ax1.plot(t, v, label="이동 속도 v(t)")
        ax1.axvline(arrival, linestyle="--", label="예상 도착 시점")
        ax1.set_title("시간에 따른 이동 속도 변화")
        ax1.set_xlabel("시간 (분)")
        ax1.set_ylabel("속도 (km/h)")
        ax1.grid(True)
        ax1.legend()

        # 누적 거리 그래프
        ax2.plot(t, s, label="누적 이동 거리 S(t)")
        ax2.axhline(D, linestyle="--", label="목적지 거리")
        ax2.axvline(arrival, linestyle=":", label="예상 도착 시점")
        ax2.set_title("시간에 따른 누적 이동 거리")
        ax2.set_xlabel("시간 (분)")
        ax2.set_ylabel("거리 (km)")
        ax2.grid(True)
        ax2.legend()

        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

        st.divider()

        # ==========================================
        # 6. 변수별 민감도 분석
        # ==========================================
        st.header("🔍 변수별 민감도 분석")
        st.write("각 변수를 기준값보다 10% 증가시켰을 때 도착시간이 어떻게 변하는지 비교합니다.")

        cases = [
            ("초기 속도 +10%", v0 * 1.1, vmin, k, D),
            ("최저 이동 속도 +10%", v0, vmin * 1.1, k, D),
            ("속도 변화 상수 +10%", v0, vmin, k * 1.1, D),
            ("목적지 거리 +10%", v0, vmin, k, D * 1.1),
        ]

        sensitivity_rows = []
        for name, a, b, c, d in cases:
            new_time = find_arrival_time(a, b, c, d)
            difference = new_time - arrival
            sensitivity_rows.append({
                "변수 변화": name,
                "예상 도착시간(분)": round(new_time, 2),
                "기준 대비 변화(분)": round(difference, 2),
            })

        st.write(f"**기준 도착시간: {arrival:.2f}분**")
        st.dataframe(
            sensitivity_rows,
            use_container_width=True,
            hide_index=True
        )

        st.info(
            "민감도 분석은 한 번에 하나의 변수만 10% 증가시키고 "
            "나머지 변수는 기준값으로 고정하여 비교한 결과입니다."
        )

    except (ValueError, OverflowError) as error:
        st.error(f"계산 중 오류가 발생했습니다: {error}")

st.divider()
st.caption("본 프로그램은 지수함수 기반의 수학적 모델을 이용한 예측 시뮬레이터이며, 실제 배달 시간과는 차이가 있을 수 있습니다.")
