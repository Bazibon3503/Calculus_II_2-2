
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "예상 도착시간",
        format_time(arrival)
    )

    col2.metric(
        "도착 시점 속도",
        f"{final_speed:.2f} km/h"
    )

    col3.metric(
        "출발 직후 속도 변화율",
        f"{initial_rate:.4f} (km/h)/분"
    )

    st.caption(
        f"목적지 거리: {D:.2f} km  |  "
        f"출발 직후 속도: {v0:.2f} km/h  |  "
        f"최저 이동 속도: {vmin:.2f} km/h"
    )

    st.divider()

    # ==========================================
    # 5. 이동 속도 및 누적 이동 거리 그래프
    # ==========================================
    st.header("📈 이동 속도 및 누적 이동 거리 그래프")

    end_time = max(30, arrival * 1.2)
    t = np.linspace(0, end_time, 400)

    v = speed(t, v0, vmin, k)
    s = distance(t, v0, vmin, k)

    fig, (ax1, ax2) = plt.subplots(
        2, 1,
        figsize=(10, 8)
    )

    # 이동 속도 그래프
    ax1.plot(t, v, label="이동 속도 v(t)")
    ax1.axvline(
        arrival,
        linestyle="--",
        label="예상 도착 시점"
    )
    ax1.set_title("시간에 따른 이동 속도 변화")
    ax1.set_xlabel("시간 (분)")
    ax1.set_ylabel("속도 (km/h)")
    ax1.grid(True)
    ax1.legend()

    # 누적 이동 거리 그래프
    ax2.plot(t, s, label="누적 이동 거리 S(t)")
    ax2.axhline(
        D,
        linestyle="--",
        label="목적지 거리"
    )
    ax2.axvline(
        arrival,
        linestyle=":",
        label="예상 도착 시점"
    )
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

    st.write(
        "각 변수를 기준값보다 10% 증가시켰을 때 "
        "예상 도착시간이 어떻게 변하는지 비교합니다."
    )

    cases = [
        ("초기 속도 +10%", v0 * 1.1, vmin, k, D),
        ("최저 이동 속도 +10%", v0, vmin * 1.1, k, D),
        ("속도 변화 상수 +10%", v0, vmin, k * 1.1, D),
        ("목적지 거리 +10%", v0, vmin, k, D * 1.1)
    ]

    sensitivity_rows = []

    for name, a, b, c, d in cases:
        new_time = find_arrival_time(a, b, c, d)
        difference = new_time - arrival

        sensitivity_rows.append({
            "변수 변화": name,
            "예상 도착시간(분)": round(new_time, 2),
            "기준 대비 변화(분)": round(difference, 2)
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

st.caption(
    "본 프로그램은 지수함수 기반의 수학적 모델을 이용한 예측 시뮬레이터이며, "
    "실제 배달 시간과는 차이가 있을 수 있습니다."
)
