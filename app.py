import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
import re
import platform

# 1. 스트림릿 페이지 기본 설정 (가장 먼저 호출되어야 합니다)
st.set_page_config(
    page_title="대학생활 심층 대시보드",
    page_icon="🎓",
    layout="wide"
)

# 2. 한글 폰트 설정 (운영체제별 한글 깨짐 방지)
if platform.system() == 'Windows':
    plt.rc('font', family='Malgun Gothic')
    font_path = 'c:/Windows/Fonts/malgun.ttf'
elif platform.system() == 'Darwin':
    plt.rc('font', family='AppleGothic')
    font_path = '/Library/Fonts/AppleGothic.ttf'
else:
    plt.rc('font', family='NanumGothic')
    font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'

# 마이너스(-) 기호가 깨지는 현상을 방지합니다.
plt.rcParams['axes.unicode_minus'] = False

# 앱 제목 및 소개글
st.title("🎓 대학생활 심층 대시보드")
st.write("대학생 설문 조사 데이터를 바탕으로 생활습관과 만족도의 관계를 분석하는 대시보드입니다.")

# 3. 사이드바 - 파일 업로드 및 필터 설정
st.sidebar.header("📁 데이터 및 필터 설정")
uploaded_file = st.sidebar.file_uploader("campus_life.csv 파일을 업로드하세요", type=["csv"])

# 파일이 업로드된 경우에만 실행
if uploaded_file is not None:
    # CSV 파일 읽기
    df_raw = pd.read_csv(uploaded_file)

    # 4. 데이터 정제 및 이상치 처리 (CSV 파일 열 이름 '스마트폰 사용시간' 띄어쓰기 반영)
    original_count = len(df_raw)  # 원본 데이터 행 개수

    # 결측치(누락값) 제거 및 음수 등 잘못된 숫자(이상치) 제거
    df_clean = df_raw.dropna(subset=['학과', '통학시간', '공부시간', '수면시간', '스마트폰 사용시간', '만족도', '한줄의견'])
    df_clean = df_clean[
        (df_clean['통학시간'] >= 0) &
        (df_clean['공부시간'] >= 0) &
        (df_clean['수면시간'] >= 0) &
        (df_clean['스마트폰 사용시간'] >= 0) &
        (df_clean['만족도'] >= 0)
        ]

    excluded_count = original_count - len(df_clean)  # 제외된 데이터 건수

    # 정제 결과 안내 메시지 출력
    st.info(f"🧹 데이터 정제 완료: 총 {original_count}건 중 **{excluded_count}건**의 잘못된 데이터가 제외되었습니다. (유효 데이터: {len(df_clean)}건)")

    # 데이터 미리보기 토글
    with st.expander("📄 업로드된 데이터 미리보기 (상단 5행)"):
        st.dataframe(df_clean.head())

    # 5. 학과 선택 필터 (사이드바)
    # '전체 보기' 옵션을 포함한 학과 리스트 생성
    majors = ['전체 보기'] + list(df_clean['학과'].unique())
    selected_major = st.sidebar.selectbox("전공(학과) 선택", majors)

    # 선택된 학과에 따라 데이터 필터링 (동적 연동)
    if selected_major == '전체 보기':
        df_filtered = df_clean
    else:
        df_filtered = df_clean[df_clean['학과'] == selected_major]

    st.divider()

    # 6. 핵심 요약 지표 (Metrics) 출력
    st.subheader(f"📌 주요 요약 지표 ({selected_major})")
    col1, col2, col3 = st.columns(3)

    total_students = len(df_filtered)
    avg_satisfaction = df_filtered['만족도'].mean() if total_students > 0 else 0
    avg_study = df_filtered['공부시간'].mean() if total_students > 0 else 0

    with col1:
        st.metric(label="👥 학생 수", value=f"{total_students}명")
    with col2:
        st.metric(label="⭐ 평균 만족도", value=f"{avg_satisfaction:.1f} 점")
    with col3:
        st.metric(label="📚 평균 공부시간", value=f"{avg_study:.1f} 시간")

    st.divider()

    # 7. 데이터 시각화 1: 산점도 (생활습관과 만족도의 관계)
    st.subheader("📊 생활습관과 만족도 관계 분석 (산점도)")

    # 분석할 생활습관 항목 선택 박스 (여기서도 스마트폰 사용시간 띄어쓰기 일치)
    habit_option = st.selectbox(
        "분석할 생활습관 항목을 선택하세요",
        ['공부시간', '수면시간', '스마트폰 사용시간', '통학시간']
    )

    if total_students > 0:
        # Matplotlib을 이용한 산점도 생성 (단위 명시)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.scatter(df_filtered[habit_option], df_filtered['만족도'], color='royalblue', alpha=0.7, s=80)
        ax.set_title(f"[{selected_major}] {habit_option}과 만족도의 관계", fontsize=14)
        ax.set_xlabel(f"{habit_option} (시간)", fontsize=12)
        ax.set_ylabel("만족도 (점)", fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.5)
        st.pyplot(fig)
    else:
        st.warning("선택한 조건에 해당하는 데이터가 없습니다.")

    st.divider()

    # 8. 데이터 시각화 2: 워드클라우드 및 상위 10개 단어 분석 (긍/부정 포함)
    st.subheader("☁️ 한 줄 의견 텍스트 분석 및 워드클라우드")

    if total_students > 0 and '한줄의견' in df_filtered.columns:
        # 한줄의견 텍스트를 하나로 합치기
        text_data = " ".join(df_filtered['한줄의견'].dropna().astype(str))

        # 2글자 이상 한글 단어 추출
        words = re.findall(r'[가-힣]{2,}', text_data)

        # 제외할 의미 없는 단어(불용어) 설정
        stopwords = ['정말', '너무', '그리고', '하지만', '에서', '으로', '것은', '하는', '있는', '입니다', '좋겠습니다']
        filtered_words = [w for w in words if w not in stopwords]

        if filtered_words:
            col_wc1, col_wc2 = st.columns(2)

            # (1) 워드클라우드 시각화 영역
            with col_wc1:
                st.markdown("#### ☁️ 워드클라우드")
                try:
                    wc = WordCloud(
                        font_path=font_path,
                        width=400,
                        height=300,
                        background_color='white',
                        colormap='winter'
                    ).generate_from_text(" ".join(filtered_words))

                    fig_wc, ax_wc = plt.subplots(figsize=(6, 4))
                    ax_wc.imshow(wc, interpolation='bilinear')
                    ax_wc.axis('off')
                    st.pyplot(fig_wc)
                except Exception as e:
                    st.error(f"워드클라우드 생성 중 오류 발생: {e}")

            # (2) 상위 10개 단어 막대그래프 및 긍/부정 카운트 영역
            with col_wc2:
                st.markdown("#### 📈 상위 10개 단어 및 긍/부정 분석")

                # 빈도수 상위 10개 단어 추출
                word_counts = Counter(filtered_words)
                top_10 = word_counts.most_common(10)

                if top_10:
                    top_words, top_freqs = zip(*top_10)

                    # 간단한 긍정/부정 키워드 분류 기준 정의
                    positive_keywords = ['좋', '만족', '행복', '즐겁', '편리', '유익', '최고', '훌륭', '감사', '도움']
                    negative_keywords = ['힘들', '어렵', '피곤', '불편', '부족', '스트레스', '지각', '나쁘', '졸려', '힘듦']

                    pos_count = 0
                    neg_count = 0
                    for w in filtered_words:
                        if any(pk in w for pk in positive_keywords):
                            pos_count += 1
                        elif any(nk in w for nk in negative_keywords):
                            neg_count += 1

                    # 긍정/부정 등장 횟수 텍스트 출력
                    st.success(f"😊 긍정 성향 단어 등장 횟수: **{pos_count}회**")
                    st.error(f"😞 부정 성향 단어 등장 횟수: **{neg_count}회**")

                    # 상위 10개 단어 막대그래프 생성
                    fig_bar, ax_bar = plt.subplots(figsize=(6, 3.5))
                    ax_bar.barh(list(top_words)[::-1], list(top_freqs)[::-1], color='teal')
                    ax_bar.set_title("자주 등장하는 상위 10개 단어", fontsize=11)
                    ax_bar.set_xlabel("등장 빈도 (회)", fontsize=9)
                    st.pyplot(fig_bar)
                else:
                    st.info("분석할 단어가 충분하지 않습니다.")
        else:
            st.info("선택한 학과 조건에 분석할 '한줄의견' 텍스트가 없습니다.")
else:
    # 파일을 아직 업로드하지 않은 경우 안내 메시지
    st.info("👈 왼쪽 사이드바에서 `campus_life.csv` 파일을 업로드하면 대시보드가 시작됩니다!")