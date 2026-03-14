import streamlit as st
import pandas as pd
import json
import uuid
import qrcode
import altair as alt
import time
from pathlib import Path

QUESTIONS_FILE = "questions.json"
RESPONSES_FILE = "responses.csv"
PARTICIPANTS_FILE = "participants.csv"
STATE_FILE = "state.json"


# ------------------------
# Helpers
# ------------------------

def load_questions():
    with open(QUESTIONS_FILE) as f:
        return json.load(f)


def load_state():
    if not Path(STATE_FILE).exists():
        state = {"started": False, "question": 0}
        save_state(state)
        return state

    with open(STATE_FILE) as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def register_participant():
    if "pid" not in st.session_state:
        pid = str(uuid.uuid4())
        st.session_state.pid = pid

        df = pd.DataFrame([[pid]], columns=["pid"])

        if Path(PARTICIPANTS_FILE).exists():
            df.to_csv(PARTICIPANTS_FILE, mode="a", header=False, index=False)
        else:
            df.to_csv(PARTICIPANTS_FILE, index=False)


def participant_count():
    if not Path(PARTICIPANTS_FILE).exists():
        return 0
    return len(pd.read_csv(PARTICIPANTS_FILE))


def save_vote(pid, qid, answer):
    df = pd.DataFrame([[pid, qid, answer]], columns=["pid", "qid", "answer"])

    if Path(RESPONSES_FILE).exists():
        df.to_csv(RESPONSES_FILE, mode="a", header=False, index=False)
    else:
        df.to_csv(RESPONSES_FILE, index=False)


def has_voted(pid, qid):
    if not Path(RESPONSES_FILE).exists():
        return False

    df = pd.read_csv(RESPONSES_FILE)
    return ((df.pid == pid) & (df.qid == qid)).any()


def results(qid):
    if not Path(RESPONSES_FILE).exists():
        return pd.DataFrame()

    df = pd.read_csv(RESPONSES_FILE)
    df = df[df.qid == qid]

    if len(df) == 0:
        return pd.DataFrame()

    counts = df.answer.value_counts().reset_index()
    counts.columns = ["option", "votes"]

    total = counts.votes.sum()
    counts["percent"] = (counts.votes / total * 100).round(1)

    return counts


def qr(url):
    img = qrcode.make(url)
    st.image(img)


# ------------------------
# Routing
# ------------------------

params = st.query_params
mode = params.get("mode", "presenter")


# ------------------------
# Presenter Landing
# ------------------------

def presenter_landing():

    st.title("Live Poll")

    url = "https://mentimeterlite-dxem3jgzxnqheyg4ncjcus.streamlit.app/?mode=participant"

    st.write("Scan to join")

    qr(url)

    st.metric("Participants", participant_count())

    if st.button("Start Poll"):
        state = load_state()
        state["started"] = True
        save_state(state)
        st.rerun()

    time.sleep(2)
    st.rerun()


# ------------------------
# Presenter Poll
# ------------------------

def presenter_poll():

    state = load_state()
    questions = load_questions()

    qid = state["question"]
    q = questions[qid]

    st.title(q["question"])

    for opt in ["A","B","C","D"]:
        st.write(q[opt])

    df = results(qid)

    if len(df) > 0:

        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X("percent", title="Percent"),
            y=alt.Y("option", sort=None),
            tooltip=["votes","percent"]
        )

        st.altair_chart(chart, use_container_width=True)

    col1,col2,col3 = st.columns(3)

    with col1:
        if st.button("Previous"):
            state["question"] -= 1
            save_state(state)
            st.rerun()

    with col2:
        if st.button("Next"):
            state["question"] += 1
            save_state(state)
            st.rerun()

    with col3:
        if st.button("Restart"):
            state["started"] = False
            state["question"] = 0
            save_state(state)

            Path(RESPONSES_FILE).unlink(missing_ok=True)
            Path(PARTICIPANTS_FILE).unlink(missing_ok=True)

            st.rerun()

    time.sleep(2)
    st.rerun()


# ------------------------
# Participant
# ------------------------

def participant():

    register_participant()

    state = load_state()

    if not state["started"]:
        st.title("Waiting for the poll to start")
        st.write("Please wait...")
        time.sleep(2)
        st.rerun()
        return

    questions = load_questions()
    qid = state["question"]
    q = questions[qid]

    st.title(q["question"])

    pid = st.session_state.pid

    if has_voted(pid, qid):
        st.success("Answer submitted")
        return

    for opt in ["A","B","C","D"]:
        if st.button(q[opt]):
            save_vote(pid, qid, opt)
            st.rerun()


# ------------------------
# App Entry
# ------------------------

state = load_state()

if mode == "participant":
    participant()

else:
    if not state["started"]:
        presenter_landing()
    else:
        presenter_poll()
