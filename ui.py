import json
import random

import streamlit as st
from streamlit import session_state

from bot2 import bot


def load_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_user(users):
    with open('users.json', 'w') as f:
        json.dump(users, f ,indent=4)


def register():
    st.subheader("Create An Account")
    name = st.text_input("Enter Your Name")
    email = st.text_input("Enter Your Email")
    password = st.text_input("Enter Your Password" , type="password")
    password = st.text_input("Enter Your Password")
    if st.button("Register👆"):
        users = load_users()
        if email in users:
            st.warning("⚠️ Email already registered.")

        else:
            users[email] = {"name": name,
                            "password": password ,
                            "score": {"Math": {"Algebra": [0, 0], "Advanced Math": [0, 0], "Problem-solving and Data Analysis": [0, 0], "Geometry and Trigonometry": [0, 0]},
                                      "Reading and Writing": {"Craft and Structure": [0, 0],"Information and Ideas": [0, 0],"Standard English Conventions": [0, 0],"Expression of Ideas": [0, 0]}},

                            "history": {
                                "Math": {
                                    "Algebra": [],
                                    "Advanced Math": [],
                                    "Problem-solving and Data Analysis": [],
                                    "Geometry and Trigonometry": []},
                                "Reading and Writing": {
                                    "Craft and Structure": [],
                                    "Information and Ideas": [],
                                    "Standard English Conventions": [],
                                    "Expression of Ideas": []}},
                            "bookmark":[]
                            }

            save_user(users)
            st.success("🥰 Successfully Registered, Now you can Login!!!")


def login():
    st.subheader("👤 Login")
    email = st.text_input("Enter Your Email")
    password = st.text_input("Enter Your Password",type="password")
    if st.button("Login"):
        users = load_users()
        if email in users and users[email]["password"] == password:
            st.session_state["user"] = email
            st.success(f"✨ Welcome {users[email]['name']}!!!")
            st.rerun()

        else:
            st.error("invalid email or password..! 😑")

def logout():
    st.session_state.pop("user", None)
    st.rerun()

def main():
    st.title("🎓 SAT AI Tutor")

    if "user" not in session_state:
        choice = st.radio("Choose an Option..!" , ["Login", "Register"])
        if choice == "Login":
            login()
        else:
            register()

    else:
        st.sidebar.success(f"Logged in as {st.session_state['user']}")

        if st.sidebar.button("Log Out"):
            logout()
        sat_app()

def sat_app():
    user_data = load_users()
    st.session_state.topic_score = user_data[st.session_state["user"]]["score"]
    st.sidebar.title("Analysis Dashboard")
    st.sidebar.header("Maths")


    for topic , scores in st.session_state.topic_score["Math"].items():
        if scores[1] != 0:
            st.sidebar.text(topic)
            st.sidebar.progress(scores[0]/scores[1])
        else:
            st.sidebar.text(topic)
            st.sidebar.progress(0)

    st.sidebar.header("Reading and Writing")

    for topic , scores in st.session_state.topic_score["Reading and Writing"].items():
        if scores[1] != 0:
            st.sidebar.text(topic)
            st.sidebar.progress(scores[0] / scores[1])
        else:
            st.sidebar.text(topic)
            st.sidebar.progress(0)

    gen_mode,random_mode ,  bookmark = st.tabs(["Generator Mode", "Random Mode" , "BookMarks"])

    with gen_mode:
        st.header("🧠 Practice Mode")

        subject = st.selectbox("Select Subject", ["Math", "Reading and Writing"])


        if subject == "Reading and Writing":
            topic = st.selectbox("Select Topic" ,["Craft and Structure","Information and Ideas","Standard English Conventions","Expression of Ideas"])

        else:
            topic = st.selectbox("Select Topic" , ["Algebra" , "Advanced Math" , "Problem-solving and Data Analysis" , "Geometry and Trigonometry"])


        difficulty = st.radio("Choose Difficulty", ["Easy", "Medium", "Hard"])
        instructions = st.text_area("Any extra instructions (optional)")

        st.session_state.current_subject = subject
        st.session_state.current_topic = topic

        history = user_data[st.session_state["user"]]["history"][st.session_state.current_subject][st.session_state.current_topic]

        if "current_question" not in st.session_state:
            st.session_state.current_question = None
            st.session_state.selected_answer = None
            st.session_state.submitted = False
            st.session_state.current_subject = None
            st.session_state.current_topic = None



        if st.button("Generate!"):
            st.session_state.score_update = False
            from bot2 import Sat_State
            state = Sat_State(
                Subject=subject,
                Topic=topic,
                Difficulty=difficulty,
                Instructions=instructions,
                Questions = None,
                History=history
            )


            result = bot.invoke(state)
            st.session_state.current_question = result["Questions"]
            user_data[st.session_state["user"]]["history"][st.session_state.current_subject][st.session_state.current_topic].append(st.session_state.current_question["question"])
            st.session_state.selected_answer = None
            st.session_state.submitted = False




        if st.session_state.current_question:
            question = session_state.current_question
            st.subheader("📕 Question")
            st.markdown(question['question'])
            options = {
                    "A" : question['option_a'],
                    "B" : question['option_b'],
                    "C" : question['option_c'],
                    "D" : question['option_d']
                }


            st.session_state.selected_answer = st.radio("Your Answer:", list(options.keys()), format_func=lambda x: f"{x}. {options[x]}",key="answer_radio")

            if st.button("Check Answer"):
                st.session_state.submitted = True


            if st.button("Bookmark 🔖"):
                bookmarked_question = st.session_state.current_question
                if bookmarked_question not in user_data[st.session_state["user"]]["bookmark"]:
                    user_data[st.session_state["user"]]["bookmark"].append(bookmarked_question)
                    save_user(user_data)
                    st.success("📘 Question added to bookmarks!")
                else:
                    st.info("✅ Already bookmarked.")


            if st.session_state.submitted:
                if st.session_state.selected_answer == question['correct_answer']:
                    if not st.session_state.score_update:
                        st.session_state.score_update = True
                        user_data[st.session_state["user"]]["score"][st.session_state.current_subject][st.session_state.current_topic][0] += 1
                        user_data[st.session_state["user"]]["score"][st.session_state.current_subject][st.session_state.current_topic][1] += 1

                    st.success("Correct!")


                else:
                    if not st.session_state.score_update:
                        st.session_state.score_update = True
                        user_data[st.session_state["user"]]["score"][st.session_state.current_subject][st.session_state.current_topic][1] += 1

                    st.error(f"❌ Wrong! Correct answer: {question['correct_answer']}")
                st.info(f"Explanation: {question['explanation']}")

            save_user(user_data)
    st.info("Generating a question may take a few seconds...")
    # placeholder = st.empty()
    # from datetime import datetime
    # import time
    # while True:
    #     now = datetime.now().strftime("%H:%M:%S")
    #
    #     # Display time
    #     placeholder.markdown(f"## 🕒 {now}")
    #
    #     # Wait 1 second
    #     time.sleep(1)

    with random_mode:
        st.header("Random Question Generator")
        st.warning("this feature is not implemented yet.")




        if "current_random_question" not in st.session_state:
            st.session_state.current_random_question = None
            st.session_state.selected_random_answer = None
            st.session_state.random_submitted = False
            st.session_state.current_random_subject = None
            st.session_state.current_random_topic = None

        if st.button("Generate random question!"):
            subject = random.choice(["Math", "Reading and Writing"])
            if subject == "Reading and Writing":
                topic = random.choice(["Craft and Structure", "Information and Ideas", "Standard English Conventions",
                                       "Expression of Ideas"])

            else:
                topic = random.choice(
                    ["Algebra", "Advanced Math", "Problem-solving and Data Analysis", "Geometry and Trigonometry"])

            difficulty = random.choice(["Easy", "Medium", "Hard"])

            st.session_state.current_random_subject = subject
            st.session_state.current_random_topic = topic
            st.session_state.current_random_difficulty = difficulty
            st.write(st.session_state.current_random_subject)
            st.text(st.session_state.current_random_topic)
            st.text(st.session_state.current_random_difficulty)

            history = user_data[st.session_state["user"]]["history"][st.session_state.current_random_subject][
                st.session_state.current_random_topic]
            st.session_state.score_update = False
            from bot2 import Sat_State
            state = Sat_State(
                Subject=subject,
                Topic=topic,
                Difficulty=difficulty,
                Instructions=instructions,
                Questions=None,
                History=history
            )

            result = bot.invoke(state)
            st.session_state.current_random_question = result["Questions"]
            user_data[st.session_state["user"]]["history"][st.session_state.current_random_subject][
                st.session_state.current_random_topic].append(st.session_state.current_random_question["question"])
            st.session_state.selected_random_answer = None
            st.session_state.random_submitted = False

        if st.session_state.current_random_question:
            question = session_state.current_random_question
            st.subheader("📕 Question")
            st.markdown(question['question'])
            options = {
                "A": question['option_a'],
                "B": question['option_b'],
                "C": question['option_c'],
                "D": question['option_d']
            }

            st.session_state.selected_random_answer = st.radio("Your Answer:", list(options.keys()),
                                                        format_func=lambda x: f"{x}. {options[x]}", key="answer_radio_random")

            if st.button("Check Answer!"):
                st.session_state.random_submitted = True

            if st.button("Bookmark 🔖!"):
                bookmarked_question = st.session_state.current_random_question
                if bookmarked_question not in user_data[st.session_state["user"]]["bookmark"]:
                    user_data[st.session_state["user"]]["bookmark"].append(bookmarked_question)
                    save_user(user_data)
                    st.success("📘 Question added to bookmarks!")
                else:
                    st.info("✅ Already bookmarked.")

            if st.session_state.random_submitted:
                if st.session_state.selected_random_answer == question['correct_answer']:
                    if not st.session_state.score_update:
                        st.session_state.score_update = True
                        user_data[st.session_state["user"]]["score"][st.session_state.current_random_subject][
                            st.session_state.current_random_topic][0] += 1
                        user_data[st.session_state["user"]]["score"][st.session_state.current_random_subject][
                            st.session_state.current_random_topic][1] += 1

                    st.success("Correct!")


                else:
                    if not st.session_state.score_update:
                        st.session_state.score_update = True
                        user_data[st.session_state["user"]]["score"][st.session_state.current_random_subject][
                            st.session_state.current_random_topic][1] += 1

                    st.error(f"❌ Wrong! Correct answer: {question['correct_answer']}")
                st.info(f"Explanation: {question['explanation']}")

            save_user(user_data)


    with bookmark:
        i = 0
        for question in user_data[st.session_state["user"]]["bookmark"][::-1]:
            i = i + 1
            st.subheader(f"{i} :")
            st.success(f"Question : {question['question']}")
            st.markdown(f"A ) {question['option_a']}")
            st.markdown(f"B ) {question['option_b']}")
            st.markdown(f"C ) {question['option_c']}")
            st.markdown(f"D ) {question['option_d']}")
            st.divider()
            st.markdown(f"Answer : {question['correct_answer']}")
            st.info(f"Explanation : {question['explanation']}")
            st.divider()
            st.divider()



if __name__ == "__main__":
    main()


