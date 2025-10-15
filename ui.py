import json
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
    password = st.text_input("Enter Your Password")
    if st.button("Register👆"):
        users = load_users()
        if email in users:
            st.warning("⚠️ Email already registered.")

        else:
            users[email] = {"name": name, "password": password , "score": 0 , "history": []}
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
    st.header("🧠 Practice Mode")
    subject = st.selectbox("Select Subject", ["Math", "Reading", "Writing"])
    topic = st.text_input("Enter Topic (e.g., Algebra, Grammar)")
    difficulty = st.radio("Choose Difficulty", ["Easy", "Medium", "Hard"])
    instructions = st.text_area("Any extra instructions (optional)")

    if "current_question" not in st.session_state:
        st.session_state.current_question = None
        st.session_state.selected_answer = None
        st.session_state.submitted = False



    if st.button("Generate!"):
        from bot2 import Sat_State
        state = Sat_State(
            Subject=subject,
            Topic=topic,
            Difficulty=difficulty,
            Instructions=instructions,
            Questions = None
        )

        result = bot.invoke(state)
        st.session_state.current_question = result["Questions"]
        st.session_state.selected_answer = None
        st.session_state.submitted = False
    if st.session_state.current_question:
        question = session_state.current_question
        st.subheader("📕 Question")
        st.write(question['question'])
        options = {
                "A" : question['option_a'],
                "B" : question['option_b'],
                "C" : question['option_c'],
                "D" : question['option_d']
            }
        st.session_state.selected_answer = st.radio("Your Answer:", list(options.keys()), format_func=lambda x: f"{x}. {options[x]}",key="answer_radio")
        if st.button("Check Answer"):
            st.session_state.submitted = True
        if st.session_state.submitted:
            if st.session_state.selected_answer == question['correct_answer']:
                st.success("Correct!")

            else:
                st.error(f"❌ Wrong! Correct answer: {question['correct_answer']}")
            st.info(f"Explanation: {question['explanation']}")

if __name__ == "__main__":
    main()


