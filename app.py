import streamlit as st
from app.auth import login_user, register_user
from app.services import generate_answer
from app.core.embeddings import get_embeddings
from app.core.vector_store import create_index
from app.utils.pdf_utils import extract_text, chunk_text

st.set_page_config(page_title="Smart Academic Assistant", layout="wide")


st.markdown("""
<style>
body {background-color: #0e1117; color: white;}
.stTextInput input, .stTextArea textarea {
    background-color: #1c1f26;
    color: white;
}
.stButton button {
    background-color: #4CAF50;
    color: white;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)


if "user" not in st.session_state:
    st.session_state.user = None

if "chat_store" not in st.session_state:
    st.session_state.chat_store = {}

if "selected_q" not in st.session_state:
    st.session_state.selected_q = None

if "chunk_map" not in st.session_state:
    st.session_state.chunk_map = []


if not st.session_state.user:
    st.title("🎓 Smart Academic Assistant")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("🔐 Login")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):
            with st.spinner("Logging in..."):
                user = login_user(username, password)
                if user:
                    st.session_state.user = username
                    st.success("Logged in!")
                else:
                    st.error("Invalid credentials")

    with tab2:
        st.subheader("📝 Register")

        full_name = st.text_input("Full Name")
        username = st.text_input("Username (Unique)")
        level = st.selectbox("Level", ["School", "College"])

        if level == "School":
            standard = st.selectbox("Standard", ["10", "11", "12"])
            department, year = "", ""
        else:
            department = st.text_input("Department")
            year = st.selectbox("Year", ["1", "2", "3", "4"])
            standard = ""

        password = st.text_input("Password", type="password")

        if st.button("Register"):
            with st.spinner("Registering..."):
                success = register_user(username, {
                    "name": full_name,
                    "password": password,
                    "level": level,
                    "standard": standard,
                    "department": department,
                    "year": year
                })

                if success:
                    st.success("✅ Registered Successfully")
                else:
                    st.error("❌ Username already exists")


else:
    user = st.session_state.user

    if user not in st.session_state.chat_store:
        st.session_state.chat_store[user] = []

    chat = st.session_state.chat_store[user]

    st.title("🎓 Smart Academic Assistant")
    st.sidebar.write(f"👤 {user}")

    if st.sidebar.button("Logout"):
        st.session_state.user = None

    st.sidebar.markdown("## 💬 Chat History")

    for i, (q, a) in enumerate(reversed(chat)):
        if st.sidebar.button(q, key=f"{user}_chat_{i}"):
            st.session_state.selected_q = (q, a)


    uploaded = st.file_uploader("Upload PDF")

    if uploaded:
        with st.spinner("Processing PDF..."):
            text = extract_text(uploaded)

            pages = text.split("\f")
            chunk_map = []

            for i, page in enumerate(pages):
                chunks = chunk_text(page)
                for c in chunks:
                    chunk_map.append({
                        "text": c,
                        "page": i + 1
                    })

            st.session_state.chunk_map = chunk_map

            all_chunks = [c["text"] for c in chunk_map]
            emb = get_embeddings(all_chunks)
            create_index(emb, all_chunks)

            st.success("✅ PDF Processed with Page Mapping")


    query = st.text_input("Ask your question")

    if st.button("Ask") and query:
        with st.spinner("Generating answer..."):
            ans, docs = generate_answer(query)

            st.session_state.chat_store[user].append((query, ans))
            st.session_state.selected_q = (query, ans)


    if st.session_state.selected_q:
        q, ans = st.session_state.selected_q

        st.markdown("## 🤖 Answer")
        st.write(ans)

 
        raw_sentences = ans.split('.')
        sentences = []
        for s in raw_sentences:
            s = s.strip()

            if len(s) < 20:
                continue
            if "###" in s or "*" in s:
                continue

            sentences.append(s)


        st.markdown("## 📌 Key Points")
        for s in sentences[:5]:
            clean_s = s.lstrip("0123456789. ").strip()
            st.write(f"• {clean_s}")


        st.markdown("## 🧠 Mindmap")

        def get_sentences(ans):
            raw = ans.replace("\n", " ").split(".")
            clean = []

            for s in raw:
                s = s.strip()

                if len(s) < 25:
                    continue
                if any(x in s.lower() for x in ["###", "***", "---"]):
                    continue

                clean.append(s)

            return clean

        sentences = get_sentences(ans)

        def pick_lines(start, count=2):
            return sentences[start:start+count] if len(sentences) > start else []

        definition = pick_lines(0, 2)
        components = pick_lines(2, 2)
        working = pick_lines(4, 2)
        types_ = pick_lines(6, 1)
        applications = pick_lines(7, 1)
        advantages = pick_lines(8, 1)

        topic = q.strip().title()[:60]

        mindmap = f"\n🧠 {topic}\n\n"

        mindmap += "├── Definition\n"
        for d in definition:
            mindmap += f"│   └── {d}\n"

        mindmap += "\n├── Key Concepts / Components\n"
        for c in components:
            mindmap += f"│   └── {c}\n"

        mindmap += "\n├── Working / Process\n"
        for w in working:
            mindmap += f"│   └── {w}\n"

        mindmap += "\n├── Types / Methods\n"
        for t in types_:
            mindmap += f"│   └── {t}\n"

        mindmap += "\n├── Applications\n"
        for a in applications:
            mindmap += f"│   └── {a}\n"

        mindmap += "\n└── Advantages / Importance\n"
        for a in advantages:
            mindmap += f"    └── {a}\n"

        st.code(mindmap)


    st.markdown("## 🎯 How this App Works")
    st.write("""
1. Upload PDF (optional)
2. Ask question
3. FAISS retrieves relevant chunks
4. Gemini generates answer
5. Chat stored per user
6. Click question to revisit answer
""")