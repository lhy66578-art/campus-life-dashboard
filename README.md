🎓 대학생활 심층 대시보드 (Campus Life Dashboard)

Streamlit과 Pandas, Matplotlib, WordCloud를 활용하여 대학생들의 생활습관(공부, 수면, 통학, 스마트폰 사용시간)과 학교생활 만족도 간의 관계를 분석하고 시각화하는 웹 애플리케이션입니다.

📌 주요 기능 (Key Features)

데이터 업로드 및 미리보기: campus_life.csv 파일 업로드 지원 및 데이터 상단 행 미리보기 기능

데이터 정제 (Data Cleaning): 누락된 값(결측치) 및 음수 시간 등의 이상치 자동 제거 후 제외된 데이터 건수 안내

학과별 동적 필터링: 사이드바의 학과 선택 드롭다운에 따라 주요 지표 및 모든 그래프 실시간 업데이트

생활습관-만족도 산점도 시각화: 항목별(공부시간, 수면시간, 스마트폰 사용시간, 통학시간)과 만족도 간의 관련성 분석

한 줄 의견 텍스트 분석:

한글 워드클라우드 시각화

빈도수 상위 10개 단어 막대그래프 출력

키워드 기반 긍정/부정 단어 등장 횟수 분석

🛠️ 기술 스택 (Tech Stack)

Language: Python 3.x

Web Framework: Streamlit

Data Processing: Pandas

Visualization: Matplotlib, WordCloud

🚀 실행 방법 (How to Run)

1. Repository 클론 및 이동

git clone https://github.com/사용자이름/저장소이름.git
cd 저장소이름

2. 패키지 설치

pip install -r requirements.txt

3. Streamlit 앱 실행

streamlit run app.py

📁 파일 구조 (Directory Structure)

app.py: Streamlit 메인 애플리케이션 코드

campus_life.csv: 설문조사 데이터 파일

requirements.txt: 필요 라이브러리 목록

README.md: 프로젝트 안내 문서
