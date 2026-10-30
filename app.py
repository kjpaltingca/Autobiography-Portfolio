"""
Developer Portfolio & Autobiography  -  Python + Streamlit
Run with:  streamlit run app.py
Edit your information in data/portfolio_data.py (not here).
"""
import html
import re
from pathlib import Path

import pandas as pd
import streamlit as st

import sys

sys.path.insert(0, str(Path(__file__).parent))          # make sure app.py's folder is importable
sys.path.insert(0, str(Path(__file__).parent / "data"))  # also allow portfolio_data.py next to a data/ folder
try:
    from data import portfolio_data as D                  # normal layout: data/portfolio_data.py
except ModuleNotFoundError:
    import portfolio_data as D                            # fallback: portfolio_data.py beside app.py

# ---------------------------------------------------------------------------
# 1. PAGE CONFIG
# ---------------------------------------------------------------------------
st.set_page_config(page_title=f"{D.PROFILE['name']} | Portfolio", page_icon="💻",
                   layout="wide", initial_sidebar_state="expanded")

ASSETS = Path(__file__).parent / "assets"
PAGES = {"home": "🏠 Home", "about": "🙋 About Me", "education": "🎓 Education", "skills": "🛠️ Skills",
         "projects": "💼 Projects", "experience": "🧳 Experience", "goals": "🎯 Career Goals",
         "contact": "✉️ Contact"}


# ---------------------------------------------------------------------------
# 2. HELPERS
# ---------------------------------------------------------------------------
def esc(x) -> str:
    return html.escape(str(x))


def go(slug: str):
    """Button callback that switches page (runs before the sidebar radio is drawn)."""
    st.session_state.nav = slug


def chips(items) -> str:
    return "".join(f'<span class="chip">{esc(i)}</span>' for i in items)


def show_image(filename: str, label: str, height: int = 180):
    """Show an image from assets/, or a styled placeholder if it is missing."""
    path = ASSETS / filename
    if path.exists():
        st.image(str(path), use_container_width=True)
    else:
        st.markdown(f'<div class="imgph" style="height:{height}px">🖼️ {esc(label)}<br>'
                    f'<small>add assets/{esc(filename)}</small></div>', unsafe_allow_html=True)


def heading(eyebrow: str, title: str, sub: str = ""):
    st.markdown(f'<div class="eyebrow">{esc(eyebrow)}</div><h1 class="sect">{esc(title)}</h1>'
                f'<p class="sub">{esc(sub)}</p><div class="rule"></div>', unsafe_allow_html=True)


def link_or_disabled(label: str, url: str, key: str):
    """Real link button when a URL exists, otherwise a disabled placeholder button."""
    if url:
        st.link_button(label, url, use_container_width=True)
    else:
        st.button(label, disabled=True, key=key, help="Add this link in data/portfolio_data.py",
                  use_container_width=True)


@st.cache_data
def all_skills_flat():
    return [(cat, s) for cat, items in D.SKILLS.items() for s in items]


@st.cache_data
def build_summary(age: int, show_age: bool) -> str:
    """Plain-text portfolio summary for the download button."""
    p = D.PROFILE
    out = [p["name"], p["headline"], p["location"]]
    if show_age:
        out.append(f"Age: {age}")
    out += ["", "EDUCATION"] + [f"- {e['program']} ({e['level']})" for e in D.EDUCATION]
    out += ["", "SKILLS"] + [f"{c}: {', '.join(s)}" for c, s in D.SKILLS.items()]
    out += ["", "PROJECTS"] + [f"- {x['title']} [{x['status']}]: {x['description']}" for x in D.PROJECTS]
    out += ["", "EXPERIENCE"] + [f"- {e['role']} - {e['company']} ({e['period']}, {e['duration']})" for e in D.EXPERIENCE]
    out += ["", "INTERESTS", ", ".join(D.INTERESTS)]
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 3. CUSTOM CSS (dark navy + cyan)
# ---------------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');
:root{--bg:#070B16;--card:rgba(17,26,46,.62);--solid:#0E1730;--ink:#E8EEF9;--muted:#8D9DBA;
      --line:rgba(120,150,210,.16);--cyan:#22D3EE;--blue:#4F8CFF;--violet:#8B5CF6;}
#MainMenu, footer{visibility:hidden;}
header[data-testid="stHeader"]{background:transparent;}
html, body, .stApp{font-family:'Inter',sans-serif;}
.stApp{color:var(--ink);
  background:
   radial-gradient(900px 500px at 85% -5%, rgba(79,140,255,.20), transparent 60%),
   radial-gradient(700px 500px at -5% 25%, rgba(34,211,238,.12), transparent 60%),
   radial-gradient(800px 600px at 60% 110%, rgba(139,92,246,.14), transparent 60%),
   var(--bg);}
.block-container{padding-top:2.2rem;max-width:1120px;}
h1,h2,h3,h4{font-family:'Space Grotesk',sans-serif !important;letter-spacing:-.01em;}

/* Sidebar */
section[data-testid="stSidebar"]{background:rgba(9,14,28,.82);backdrop-filter:blur(14px);
  border-right:1px solid var(--line);}
section[data-testid="stSidebar"] div[role="radiogroup"]{gap:.2rem;}
section[data-testid="stSidebar"] div[role="radiogroup"] label{padding:.5rem .8rem;border-radius:12px;
  transition:background .2s, transform .2s;width:100%;}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover{background:rgba(34,211,238,.10);transform:translateX(3px);}
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked){
  background:linear-gradient(90deg,rgba(34,211,238,.20),rgba(79,140,255,.08));border:1px solid rgba(34,211,238,.35);}

/* Headings */
.eyebrow{color:var(--cyan);letter-spacing:.22em;text-transform:uppercase;font-size:.72rem;font-weight:600;}
h1.sect{font-size:2.7rem;margin:.15rem 0 0;padding:0;background:linear-gradient(90deg,#fff,#9FB6E8);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.sub{color:var(--muted);margin:.25rem 0 0;}
.rule{height:3px;width:64px;background:linear-gradient(90deg,var(--cyan),var(--violet));border-radius:3px;margin:.7rem 0 1.6rem;}

/* Hero */
.hero{position:relative;overflow:hidden;background:linear-gradient(145deg,rgba(24,38,72,.75),rgba(12,18,36,.75));
  border:1px solid var(--line);border-radius:28px;padding:2.6rem;backdrop-filter:blur(10px);
  box-shadow:0 24px 60px rgba(0,0,0,.5), inset 0 1px 0 rgba(255,255,255,.06);}
.hero::after{content:'';position:absolute;right:-80px;top:-80px;width:260px;height:260px;border-radius:50%;
  background:radial-gradient(circle,rgba(34,211,238,.35),transparent 70%);filter:blur(10px);}
.hero h1{font-size:3.3rem;line-height:1.05;margin:.4rem 0;padding:0;}
.hero .grad{background:linear-gradient(90deg,var(--cyan),var(--blue),var(--violet));-webkit-background-clip:text;
  -webkit-text-fill-color:transparent;}
.hero h3{font-weight:500;}

/* Cards (glass) */
.card{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:1.2rem 1.4rem;
  backdrop-filter:blur(10px);box-shadow:0 10px 30px rgba(0,0,0,.28);margin-bottom:1rem;
  transition:transform .25s, border-color .25s, box-shadow .25s;}
.card:hover{transform:translateY(-3px);border-color:rgba(34,211,238,.5);box-shadow:0 16px 40px rgba(34,211,238,.10);}
.muted{color:var(--muted);}
.chip{display:inline-block;border:1px solid rgba(34,211,238,.28);background:rgba(34,211,238,.07);color:#9BE8F6;
  border-radius:999px;padding:.18rem .8rem;margin:.2rem .3rem .2rem 0;font-size:.8rem;font-weight:500;}
.status{display:inline-block;background:linear-gradient(90deg,rgba(34,211,238,.18),rgba(139,92,246,.18));
  color:#BFEFFA;border:1px solid rgba(34,211,238,.3);border-radius:999px;padding:.1rem .7rem;font-size:.72rem;font-weight:600;}

/* Images */
.stImage img{border-radius:22px;border:1px solid var(--line);box-shadow:0 18px 44px rgba(0,0,0,.5), 0 0 0 6px rgba(34,211,238,.06);}
.imgph{display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;
  border:1.5px dashed rgba(120,150,210,.35);border-radius:22px;color:var(--muted);
  background:repeating-linear-gradient(45deg,rgba(255,255,255,.015),rgba(255,255,255,.015) 10px,transparent 10px,transparent 20px);}

/* Timeline */
.tl{border-left:2px solid transparent;border-image:linear-gradient(180deg,var(--cyan),var(--violet)) 1;
  margin-left:.5rem;padding-left:1.5rem;}
.tli{position:relative;background:var(--card);border:1px solid var(--line);border-radius:16px;
  padding:1rem 1.3rem;margin-bottom:1rem;backdrop-filter:blur(10px);transition:transform .25s,border-color .25s;}
.tli:hover{transform:translateX(4px);border-color:rgba(34,211,238,.5);}
.tli::before{content:'';position:absolute;left:-2.15rem;top:1.3rem;width:13px;height:13px;
  background:var(--cyan);border-radius:50%;border:3px solid var(--bg);box-shadow:0 0 14px var(--cyan);}
.tlmeta{font-size:.74rem;color:var(--cyan);font-weight:600;letter-spacing:.08em;text-transform:uppercase;}
.tli h4{margin:.15rem 0;padding:0;} .tli p{margin:.2rem 0;color:var(--muted);}

/* Buttons */
.stButton>button,.stDownloadButton>button,.stFormSubmitButton>button,.stLinkButton>a{border-radius:999px;
  border:1px solid rgba(34,211,238,.45);background:rgba(34,211,238,.06);font-weight:600;transition:all .22s;}
.stButton>button:hover:not(:disabled),.stDownloadButton>button:hover,.stFormSubmitButton>button:hover,
.stLinkButton>a:hover{background:linear-gradient(90deg,var(--cyan),var(--blue));color:#05101f !important;
  border-color:transparent;transform:translateY(-2px);box-shadow:0 10px 24px rgba(34,211,238,.28);}
.stButton>button[kind="primary"]{background:linear-gradient(90deg,var(--cyan),var(--blue));color:#05101f;border:none;}
.stButton>button:disabled{opacity:.45;border-style:dashed;}

/* Widgets */
div[data-testid="stMetric"]{background:var(--card);border:1px solid var(--line);border-radius:16px;
  padding:.9rem 1.1rem;backdrop-filter:blur(10px);}
div[data-testid="stMetricValue"]{font-family:'Space Grotesk',sans-serif;
  background:linear-gradient(90deg,var(--cyan),var(--blue));-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
div[data-testid="stExpander"]{background:var(--card);border:1px solid var(--line);border-radius:14px;}
div[data-testid="stVerticalBlockBorderWrapper"]:has(> div > div > div > .stImage),
div[data-testid="stVerticalBlockBorderWrapper"]{border-radius:18px;}
.stTabs [data-baseweb="tab-list"]{gap:.3rem;border-bottom:1px solid var(--line);}
.stTabs [data-baseweb="tab"]{font-weight:600;border-radius:10px 10px 0 0;padding:.5rem 1rem;}
.stTabs [aria-selected="true"]{color:var(--cyan);}
.stTextInput input, .stTextArea textarea, .stNumberInput input, div[data-baseweb="select"]>div{
  border-radius:12px !important;background:rgba(14,23,48,.7) !important;border:1px solid var(--line) !important;}
.stTextInput input:focus, .stTextArea textarea:focus{border-color:var(--cyan) !important;box-shadow:0 0 0 3px rgba(34,211,238,.15) !important;}
div[data-testid="stProgress"] div[role="progressbar"] > div{background:linear-gradient(90deg,var(--cyan),var(--violet));}
hr{border-color:var(--line) !important;}
.foot{text-align:center;color:var(--muted);font-size:.85rem;padding:2.5rem 0 .5rem;}
::-webkit-scrollbar{width:8px;} ::-webkit-scrollbar-thumb{background:#1F2D4A;border-radius:8px;}
</style>
"""


# ---------------------------------------------------------------------------
# 4. PAGES
# ---------------------------------------------------------------------------
def page_home():
    p = D.PROFILE
    show_age = st.session_state.show_age
    left, right = st.columns([1.6, 1], gap="large")
    with left:
        age_txt = f" · {st.session_state.age} years old" if show_age else ""
        st.markdown(
            f'<div class="hero"><div class="eyebrow">Hello, world 👋</div>'
            f'<h1>I\'m <span class="grad">{esc(p["name"])}</span></h1>'
            f'<h3 class="muted">{esc(p["headline"])}</h3><p>{esc(p["intro"])}</p>'
            f'<p class="muted">📍 {esc(p["location"])}{esc(age_txt)}</p>'
            f'{chips(["Software Development", "Game Development"])}</div>', unsafe_allow_html=True)
        st.write("")
        b1, b2 = st.columns(2)
        b1.button("🚀 Explore my projects", on_click=go, args=("projects",), use_container_width=True, type="primary")
        b2.button("✉️ Contact me", on_click=go, args=("contact",), use_container_width=True)
    with right:
        show_image("profile.jpg", "Profile picture", 340)

    st.write("")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Projects", len(D.PROJECTS))
    m2.metric("Skills listed", len(all_skills_flat()))
    m3.metric("Work roles", len(D.EXPERIENCE))
    m4.metric("Interests", len(D.INTERESTS))

    st.divider()
    cols = st.columns(len(D.SOCIALS))
    for col, (name, url) in zip(cols, D.SOCIALS.items()):
        with col:
            link_or_disabled(name, url, f"home_{name}")


def page_about():
    heading("Get to know me", "About Me", "My story so far.")
    tab1, tab2, tab3 = st.tabs(["📖 My Story", "📋 Quick Facts", "🎮 Interests"])
    with tab1:
        for para in D.ABOUT_PARAGRAPHS:
            st.markdown(f'<div class="card">{esc(para)}</div>', unsafe_allow_html=True)
    with tab2:
        p = D.PROFILE
        rows = {"Name": p["name"], "Location": p["location"], "Course": p["course"],
                "Year level": p["year_level"], "Career interest": p["career_interest"]}
        if st.session_state.show_age:
            rows["Age"] = st.session_state.age
        st.table(pd.DataFrame({"Detail": list(rows), "Value": [str(v) for v in rows.values()]}).set_index("Detail"))
        with st.popover("ℹ️ Why is Age editable?"):
            st.write("Change or hide it from the sidebar settings. It is not saved permanently; "
                     "edit `PROFILE['age']` in `data/portfolio_data.py`.")
    with tab3:
        st.markdown(chips(D.INTERESTS), unsafe_allow_html=True)
        pick = st.selectbox("Learn more about an interest", D.INTERESTS)
        st.info(f"**{pick}** is one of my interests. Add a short description in `data/portfolio_data.py` if you like.")


def page_education():
    heading("Academic path", "Education", "From Electronics Engineering to Information Technology.")
    view = st.radio("View as", ["Timeline", "Table"], horizontal=True)
    if view == "Timeline":
        out = '<div class="tl">'
        for e in D.EDUCATION:
            out += (f'<div class="tli"><div class="tlmeta">{esc(e["level"])} · {esc(e["years"])}</div>'
                    f'<h4>{esc(e["program"])}</h4><p>{esc(e["school"])}</p><p>{esc(e["note"])}</p></div>')
        st.markdown(out + "</div>", unsafe_allow_html=True)
        st.caption("Items that say “Add …” are editable placeholders.")
    else:
        st.dataframe(pd.DataFrame(D.EDUCATION), use_container_width=True, hide_index=True)


def page_skills():
    heading("Toolbox", "Technical Skills", "What I work with. Proficiency is set by me, never assumed.")
    levels = st.session_state.levels
    edit = st.checkbox("✏️ Edit proficiency levels (this session)")
    tabs = st.tabs(list(D.SKILLS))
    for tab, (cat, items) in zip(tabs, D.SKILLS.items()):
        with tab:
            cols = st.columns(3)
            for i, skill in enumerate(items):
                with cols[i % 3].container(border=True):
                    st.markdown(f"**{skill}**")
                    if edit:
                        levels[skill] = st.slider("Level", 0, 100, levels.get(skill, 0), 5, key=f"lvl_{skill}",
                                                  label_visibility="collapsed")
                    if levels.get(skill):
                        st.progress(levels[skill] / 100, text=f"{levels[skill]}%")
                    else:
                        st.caption("Level not set")
    st.divider()
    st.subheader("Skills overview")
    counts = pd.DataFrame({"Category": list(D.SKILLS), "Skills": [len(v) for v in D.SKILLS.values()]}).set_index("Category")
    st.bar_chart(counts)
    rated = {k: v for k, v in levels.items() if v}
    if rated:
        st.subheader("My self-rated levels")
        st.bar_chart(pd.Series(rated, name="Level"))


def page_projects():
    heading("Selected work", "Projects", "Concepts and builds I have worked on.")
    cats = sorted({p["category"] for p in D.PROJECTS})
    f1, f2 = st.columns([1, 2])
    query = f1.text_input("🔍 Search", placeholder="Title or technology")
    chosen = f2.multiselect("Categories", cats, default=cats)
    results = [p for p in D.PROJECTS if p["category"] in chosen
               and query.lower() in (p["title"] + " ".join(p["tech"])).lower()]
    st.caption(f"Showing {len(results)} of {len(D.PROJECTS)} projects")
    if not results:
        st.warning("No projects match your filters.")
    cols = st.columns(2)
    for i, p in enumerate(results):
        with cols[i % 2].container(border=True):
            show_image(p["image"], p["title"], 160)
            st.markdown(f"### {p['title']}")
            st.markdown(f'<span class="status">{esc(p["status"])}</span> <span class="muted">· {esc(p["category"])}</span>',
                        unsafe_allow_html=True)
            st.write(p["description"])
            st.markdown(chips(p["tech"]), unsafe_allow_html=True)
            with st.expander("Main features"):
                for f in p["features"]:
                    st.markdown(f"- {f}")
            link_or_disabled("💻 GitHub repository", p["github"], f"gh_{p['title']}")


def page_experience():
    heading("Where I've worked", "Experience", "Customer service, virtual assistance, and invoice processing.")
    out = '<div class="tl">'
    for e in D.EXPERIENCE:
        out += (f'<div class="tli"><div class="tlmeta">{esc(e["period"])} · {esc(e["duration"])}</div>'
                f'<h4>{esc(e["role"])}</h4><p>{esc(e["company"])}</p></div>')
    st.markdown(out + "</div>", unsafe_allow_html=True)
    for e in D.EXPERIENCE:
        with st.expander(f"Details: {e['role']} ({e['company']})"):
            for d in e["details"]:
                st.markdown(f"- {d}")


def goal_list(goals, prefix: str):
    done = 0
    for i, g in enumerate(goals):
        if st.checkbox(g, key=f"{prefix}_{i}"):
            done += 1
    st.progress(done / len(goals), text=f"{done} of {len(goals)} marked done by me")


def page_goals():
    heading("What's next", "Career Goals", "Where I'm heading. Tick goals as I achieve them.")
    horizon = st.radio("Horizon", ["Both", "Short-term", "Long-term"], horizontal=True)
    c1, c2 = st.columns(2, gap="large")
    if horizon in ("Both", "Short-term"):
        with c1:
            st.subheader("⚡ Short-term")
            goal_list(D.SHORT_TERM_GOALS, "short")
    if horizon in ("Both", "Long-term"):
        with c2:
            st.subheader("🌟 Long-term")
            goal_list(D.LONG_TERM_GOALS, "long")
    st.info(f"Career interest: **{D.PROFILE['career_interest']}**")


def valid_email(s: str) -> bool:
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", s))


def page_contact():
    heading("Say hello", "Contact", "Send a message or find me online.")
    c1, c2 = st.columns([1, 1.5], gap="large")
    with c1:
        for name, url in D.SOCIALS.items():
            link_or_disabled(name, url, f"contact_{name}")
        st.download_button("⬇️ Download portfolio summary",
                           build_summary(st.session_state.age, st.session_state.show_age),
                           file_name="portfolio_summary.txt", use_container_width=True)
        resume = ASSETS / "resume.pdf"
        if resume.exists():
            st.download_button("⬇️ Download resume (PDF)", resume.read_bytes(), file_name="resume.pdf",
                               mime="application/pdf", use_container_width=True)
    with c2:
        with st.form("contact_form", clear_on_submit=True):
            name = st.text_input("Your name")
            email = st.text_input("Email address")
            subject = st.text_input("Subject")
            message = st.text_area("Message", height=140)
            sent = st.form_submit_button("Send message")
        if sent:
            errors = []
            if len(name.strip()) < 2:
                errors.append("Please enter your name.")
            if not valid_email(email):
                errors.append("Please enter a valid email address.")
            if len(subject.strip()) < 3:
                errors.append("Subject is too short.")
            if len(message.strip()) < 10:
                errors.append("Message must be at least 10 characters.")
            if errors:
                for e in errors:
                    st.error(e)
            else:
                st.session_state.messages.append({"name": name, "email": email, "subject": subject})
                st.success(f"Thank you, {name.strip()}! Your message was received.")
                st.toast("Message submitted", icon="✅")
                st.caption("Demo form: messages are not emailed anywhere.")


# ---------------------------------------------------------------------------
# 5. MAIN: state, sidebar, routing
# ---------------------------------------------------------------------------
ROUTES = {"home": page_home, "about": page_about, "education": page_education, "skills": page_skills,
          "projects": page_projects, "experience": page_experience, "goals": page_goals, "contact": page_contact}


def main():
    # Session state defaults
    st.session_state.setdefault("age", D.PROFILE["age"])
    st.session_state.setdefault("show_age", True)
    st.session_state.setdefault("levels", dict(D.SKILL_LEVELS))
    st.session_state.setdefault("messages", [])
    if "nav" not in st.session_state:  # restore page from URL (?page=skills)
        qp = st.query_params.get("page", "home")
        st.session_state.nav = qp if qp in PAGES else "home"

    st.markdown(CSS, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(f"### 💻 {D.PROFILE['name'].split()[0]} {D.PROFILE['name'].split()[1]}")
        st.caption(D.PROFILE["headline"])
        st.radio("Navigate", list(PAGES), format_func=lambda k: PAGES[k], key="nav")
        st.divider()
        with st.expander("⚙️ Settings"):
            st.toggle("Show age", key="show_age")
            st.number_input("Age", 10, 100, key="age")
        st.caption(f"Messages sent this session: {len(st.session_state.messages)}")

    st.query_params["page"] = st.session_state.nav
    ROUTES[st.session_state.nav]()
    st.markdown(f'<div class="foot">© {D.PROFILE["name"]} · Built with Python & Streamlit</div>', unsafe_allow_html=True)


main()
