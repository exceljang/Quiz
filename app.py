import streamlit as st
import pandas as pd
from PIL import Image
import random
import json
import os

# 페이지 설정
st.set_page_config(
    page_title="한국 야생화 퀴즈",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 세션 상태 초기화
def init_session_state():
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'total_questions' not in st.session_state:
        st.session_state.total_questions = 10
    if 'game_started' not in st.session_state:
        st.session_state.game_started = False
    if 'difficulty' not in st.session_state:
        st.session_state.difficulty = "초급"
    if 'questions' not in st.session_state:
        st.session_state.questions = []

# 문제 데이터 로드
def load_questions():
    try:
        with open('questions.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 난이도에 따라 문제 필터링
            filtered_questions = [q for q in data['questions'] if q['difficulty'] == st.session_state.difficulty]
            if not filtered_questions:
                st.error(f"{st.session_state.difficulty} 난이도의 문제가 없습니다. 다른 난이도를 선택해주세요.")
                return []
            
            # 사용 가능한 문제 수 확인
            available_questions = len(filtered_questions)
            if available_questions < st.session_state.total_questions:
                st.warning(f"선택한 난이도의 문제가 {available_questions}개 밖에 없습니다. 문제 수를 조정합니다.")
                st.session_state.total_questions = available_questions
            
            # 문제 순서를 랜덤으로 섞기
            random.shuffle(filtered_questions)
            
            # 선택한 문제 수만큼 반환
            return filtered_questions[:st.session_state.total_questions]
    except FileNotFoundError:
        st.error("문제 데이터 파일(questions.json)을 찾을 수 없습니다.")
        return []
    except json.JSONDecodeError:
        st.error("문제 데이터 파일의 형식이 잘못되었습니다.")
        return []
    except Exception as e:
        st.error(f"문제 데이터를 불러오는 중 오류가 발생했습니다: {str(e)}")
        return []

# 이미지 로드 함수
def load_image(image_path):
    try:
        if not os.path.exists(image_path):
            st.error(f"이미지 파일을 찾을 수 없습니다: {image_path}")
            return None
        return Image.open(image_path)
    except Exception as e:
        st.error(f"이미지를 불러오는 중 오류가 발생했습니다: {str(e)}")
        return None

# 메인 페이지
def main():
    # 세션 상태 초기화
    init_session_state()
    
    st.title("🌸 한국 야생화 퀴즈 🌸")
    
    if not st.session_state.game_started:
        st.write("한국의 아름다운 야생화를 알아보세요!")
        st.write("각 문제에서 보여주는 야생화의 이름을 맞춰보세요.")
        
        # 난이도 선택
        st.session_state.difficulty = st.selectbox(
            "난이도를 선택하세요",
            ["초급", "중급", "고급"]
        )
        
        # 문제 수 선택
        st.session_state.total_questions = st.slider(
            "문제 수를 선택하세요",
            min_value=5,
            max_value=20,
            value=10,
            step=5
        )
        
        if st.button("게임 시작하기"):
            questions = load_questions()
            if questions:  # 문제가 있는 경우에만 게임 시작
                st.session_state.game_started = True
                st.session_state.score = 0
                st.session_state.current_question = 0
                st.session_state.questions = questions
                st.rerun()
    else:
        if not st.session_state.questions:  # 문제가 없는 경우
            st.error("문제를 불러올 수 없습니다. 다시 시작해주세요.")
            if st.button("다시 시작하기"):
                st.session_state.game_started = False
                st.rerun()
        elif st.session_state.current_question < len(st.session_state.questions):
            current_q = st.session_state.questions[st.session_state.current_question]
            
            # 진행 상황 표시
            col1, col2 = st.columns([3, 1])
            with col1:
                st.progress(st.session_state.current_question / len(st.session_state.questions))
            with col2:
                st.write(f"현재 점수: {st.session_state.score}")
            
            st.write(f"문제 {st.session_state.current_question + 1}/{len(st.session_state.questions)}")
            
            # 이미지 표시
            image = load_image(current_q["image_url"])
            if image:
                # 이미지 크기 조정
                max_width = 400
                ratio = max_width / image.width
                new_height = int(image.height * ratio)
                resized_image = image.resize((max_width, new_height))
                st.image(resized_image, use_container_width=False)
            
            # 선택지 표시
            selected = st.radio("이 야생화의 이름은 무엇일까요?", current_q["options"], horizontal=True, index=None)
            
            if selected is not None:
                if selected == current_q["correct_answer"]:
                    st.success("정답입니다! 🎉")
                    st.write(f"설명: {current_q['description']}")
                    st.session_state.score += 1
                else:
                    st.error(f"틀렸습니다. 정답은 {current_q['correct_answer']}입니다.")
                    st.write(f"설명: {current_q['description']}")
                
                if st.button("다음 문제"):
                    st.session_state.current_question += 1
                    st.rerun()
        else:
            # 게임 종료 화면
            st.balloons()
            st.write(f"🎉 게임이 끝났습니다! 🎉")
            st.write(f"최종 점수: {st.session_state.score}/{len(st.session_state.questions)}")
            
            # 정답률 계산
            percentage = (st.session_state.score / len(st.session_state.questions)) * 100
            st.write(f"정답률: {percentage:.1f}%")
            
            if st.button("다시 시작하기"):
                st.session_state.game_started = False
                st.rerun()

if __name__ == "__main__":
    main() 