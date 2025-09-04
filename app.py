import streamlit as st
from pathlib import Path
from src.generator import ExcuseGenerator, ExcuseRequest


APP_TITLE = "Excuse Generator"
APP_TAGLINE = "Generate polished, context-aware excuses in seconds"


def initialize_session_state() -> None:
    if "history" not in st.session_state:
        st.session_state["history"] = []
    if "persist_dir" not in st.session_state:
        st.session_state["persist_dir"] = str(Path(".history").resolve())


def render_header() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon="📝", layout="centered")

    # Minimal, grayscale-only styling for a clean, energetic look without colors
    st.markdown(
        """
        <style>
        .app-header h1 { margin-bottom: 0.2rem; letter-spacing: 0.3px; }
        .app-header p { margin-top: 0.2rem; font-size: 0.95rem; opacity: 0.85; }
        .card {
            border: 1px solid rgba(0,0,0,0.08);
            border-radius: 12px;
            padding: 1rem 1rem;
        }
        .chips { display: flex; gap: 0.5rem; flex-wrap: wrap; }
        .chips .chip-btn button {
            border-radius: 999px !important;
            padding: 0.25rem 0.75rem !important;
        }
        .mono-hint { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; opacity: 0.75; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="app-header">
          <h1>📝 Excuse Generator</h1>
          <p>Simple words. Clear tone. Ready to send.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_controls() -> ExcuseRequest:
    st.sidebar.header("⚙️ Controls")

    category = st.sidebar.selectbox(
        "Scenario",
        [
            "Work Deadline",
            "School Assignment",
            "Social Event",
            "Appointment",
            "Travel/Commute",
            "General",
        ],
        index=0,
    )

    audience = st.sidebar.selectbox(
        "Audience",
        ["Manager", "Professor", "Friend", "Family", "Client", "Other"],
        index=0,
    )

    tone = st.sidebar.selectbox(
        "Tone",
        ["Professional", "Casual", "Sincere", "Brief", "Light-hearted"],
        index=0,
    )

    specificity = st.sidebar.slider(
        "Specificity", 0, 10, 6, help="Higher values add more concrete details"
    )

    length = st.sidebar.radio("Length", ["Short", "Medium", "Long"], index=1)

    custom_context = st.sidebar.text_area(
        "Optional context",
        placeholder="Key details (project name, course, event, constraints)",
        height=80,
    )

    seed = st.sidebar.number_input("Random seed (optional)", value=0, step=1, min_value=0)

    st.sidebar.markdown("---")
    persist_history = st.sidebar.checkbox("Save history to disk", value=False)
    persist_dir = st.sidebar.text_input("History folder", value=st.session_state["persist_dir"]) if persist_history else None

    return ExcuseRequest(
        category=category,
        audience=audience,
        tone=tone,
        specificity=int(specificity),
        length=length,
        custom_context=custom_context.strip(),
        seed=int(seed) if seed else None,
        persist_history=persist_history,
        persist_dir=persist_dir,
    )


def render_output_area(generator: ExcuseGenerator, request: ExcuseRequest) -> None:
    tabs = st.tabs(["✍️ Generate", "📜 History", "⚡ Tips"])

    with tabs[0]:
        st.markdown("### Your excuse")

        # Quick picks to keep the flow playful yet focused
        st.markdown("**Quick picks**")
        qp_cols = st.columns(4)
        with qp_cols[0]:
            if st.button("Short", use_container_width=True):
                request.length = "Short"
        with qp_cols[1]:
            if st.button("Medium", use_container_width=True):
                request.length = "Medium"
        with qp_cols[2]:
            if st.button("Long", use_container_width=True):
                request.length = "Long"
        with qp_cols[3]:
            if st.button("Sincere", use_container_width=True):
                request.tone = "Sincere"

        st.divider()

        cols = st.columns([1, 1, 1])
        with cols[0]:
            generate_clicked = st.button("Generate", type="primary")
        with cols[1]:
            rephrase_clicked = st.button("Rephrase")
        with cols[2]:
            copy_clicked = st.button("Copy")

        if generate_clicked:
            result = generator.generate(request)
            st.session_state["current_excuse"] = result
            st.session_state["history"].append(result)
            if request.persist_history:
                generator.persist(result)

        if rephrase_clicked and st.session_state.get("current_excuse"):
            result = generator.rephrase(request, st.session_state["current_excuse"])  
            st.session_state["current_excuse"] = result
            st.session_state["history"].append(result)
            if request.persist_history:
                generator.persist(result)

        current = st.session_state.get("current_excuse", "")
        st.markdown("#### Output")
        st.text_area("Excuse text", value=current, height=180, label_visibility="collapsed")
        st.caption("Press Ctrl/Cmd+C to copy."
                   "  ")
        if copy_clicked and current:
            st.toast("Copied to clipboard (select + Ctrl/Cmd+C)")

    with tabs[1]:
        st.markdown("### Recent history")
        if not st.session_state["history"]:
            st.info("No history yet. Generate an excuse to see it here.")
        else:
            for idx, item in enumerate(reversed(st.session_state["history"])):
                st.markdown(f"{len(st.session_state['history']) - idx}. {item}")

    with tabs[2]:
        st.markdown("### Tips")
        st.markdown(
            "- Keep it short when you're unsure.\n"
            "- Add one concrete detail for trust.\n"
            "- Be clear about the new time or next step."
        )


def main() -> None:
    initialize_session_state()
    render_header()
    request = render_sidebar_controls()
    generator = ExcuseGenerator()
    render_output_area(generator, request)


if __name__ == "__main__":
    main()


