from __future__ import annotations
import json, random, sys, time, uuid, platform
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List

import pandas as pd
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ───────────────────────── paths / constants
BASE_DIR          = Path(__file__).resolve().parent
STIMULI_PATH      = BASE_DIR / "stimuli.json"
IMAGES_DIR        = BASE_DIR / "images"
LOG_DIR           = BASE_DIR / "logs"; LOG_DIR.mkdir(exist_ok=True)
LOCAL_CSV         = LOG_DIR / "responses.csv"
GOOGLE_SHEET_NAME = "Trivia_Responses"
GOOGLE_SHEET_TAB  = "Responses"

N_TRUE, N_FALSE, N_PHOTO_EACH = 8, 8, 4

# ───────────────────────── Google Sheets helper
def save_to_google_sheets(df: pd.DataFrame) -> None:
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            st.secrets["GSPREAD_KEY"],
            ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"],
        )
        gspread.authorize(creds) \
               .open(GOOGLE_SHEET_NAME) \
               .worksheet(GOOGLE_SHEET_TAB) \
               .append_rows(df.astype(str).values.tolist())
    except Exception as e:
        st.warning(f"⚠️ Google‑Sheets write failed: {e}")

# ───────────────────────── stimulus model
@dataclass
class Stimulus:
    id: str; text: str; truth: bool; photo: str | None; show_photo: bool = False
    @property
    def has_photo(self): return self.photo and self.photo.endswith(".png")
    @property
    def image_path(self): return IMAGES_DIR/self.photo if self.has_photo else None

def load_stimuli() -> List[Stimulus]:
    return [Stimulus(**d) for d in json.load(STIMULI_PATH.open())]

def create_subset(pool: List[Stimulus]) -> List[Stimulus]:
    tr = random.sample([s for s in pool if s.truth],  N_TRUE)
    fl = random.sample([s for s in pool if not s.truth], N_FALSE)
    combo = tr + fl; random.shuffle(combo)
    with_photo = [s for s in combo if s.has_photo]; random.shuffle(with_photo)
    t=f=0
    for s in with_photo:
        if s.truth and t<N_PHOTO_EACH: s.show_photo=True; t+=1
        elif not s.truth and f<N_PHOTO_EACH: s.show_photo=True; f+=1
        if t==N_PHOTO_EACH and f==N_PHOTO_EACH: break
    return combo

# ───────────────────────── Streamlit init
st.set_page_config("Truth Perception Study", "🤔", "centered")

# ► only new‑API ◄
if "variant" not in st.query_params:
    st.query_params["variant"] = random.choice(["A", "B"])
VARIANT = st.query_params["variant"]
BUTTON_OPTS = {"type": "primary", "use_container_width": VARIANT == "B"}

# optional GA (avoids st.components)
if ga_id := st.secrets.get("GA_MEASUREMENT_ID"):
    st.markdown(
        f"""
        <script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){{dataLayer.push(arguments);}}
          gtag('js', new Date());
          gtag('config', '{ga_id}');
        </script>
        """,
        unsafe_allow_html=True,
    )

# ───────────────────────── session defaults
ss = st.session_state
ss.setdefault("participant_id", str(uuid.uuid4()))
ss.setdefault("prompt_group", random.choice(["Explain", "Emotion"]))
ss.setdefault("stimuli", create_subset(load_stimuli()))
ss.setdefault("responses", [])
ss.setdefault("index", 0)
ss.setdefault("start_time", None)

# ───────────────────────── UI helpers
def show_instructions():
    st.markdown("### Instructions")
    st.info(
        "Judge each statement **True/False**, then "
        + ("explain your reasoning." if ss.prompt_group=="Explain"
           else "describe your feelings.")
    )
    if st.button("Start", **BUTTON_OPTS):
        ss.show_instructions=False
        st.rerun()

def run_trial(stim: Stimulus,i:int,total:int):
    st.subheader(f"Statement {i}/{total}")
    st.write(stim.text)
    if stim.show_photo and stim.image_path and stim.image_path.exists():
        st.image(stim.image_path.read_bytes(), width=320)

    if ss.start_time is None: ss.start_time=time.time()
    with st.form(f"f_{stim.id}"):
        ans = st.radio("Is the statement…",["True","False"],horizontal=True)
        txt = st.text_area("Explain:" if ss.prompt_group=="Explain" else "Feelings:", height=120)
        if st.form_submit_button("Submit & Next", **BUTTON_OPTS):
            if not txt.strip(): st.warning("Text box cannot be empty."); st.stop()
            rt = round(time.time()-ss.start_time, 2); ss.start_time=None
            ss.responses.append(dict(
                timestamp=datetime.utcnow().isoformat(),
                participant_id=ss.participant_id, variant=VARIANT,
                prompt_group=ss.prompt_group, stimulus_id=stim.id,
                truth=stim.truth, answer=ans=="True",
                correct=(ans=="True")==stim.truth, response_text=txt.strip(),
                show_photo=stim.show_photo, rt=rt,
                py=sys.version.split()[0], platform=platform.platform(),
                streamlit=st.__version__
            ))
            ss.index += 1; st.rerun()

def finish():
    st.balloons(); st.success("✔️ Responses saved — thank you!")
    df = pd.DataFrame(ss.responses)
    if LOCAL_CSV.exists(): df = pd.concat([pd.read_csv(LOCAL_CSV), df], ignore_index=True)
    df.to_csv(LOCAL_CSV, index=False)
    save_to_google_sheets(df)

    st.markdown("### Quick stats (session)"); st.dataframe(df[["stimulus_id","correct","rt"]])

    st.markdown("### Debriefing")
    st.markdown("""
    Thank you for completing this short trivia survey!

    This study is part of a research project investigating how visual cues (like unrelated photos) and different kinds of reasoning (**explanation** vs. **emotion**) affect people’s perception of truth.

    Some of the statements you saw were factually accurate, while others were not, and some were paired with images that were not directly related to the content. By analysing how people respond under different conditions, we hope to better understand how misinformation spreads online—especially when it is accompanied by persuasive visuals.

    Your responses have been recorded **anonymously** and will help support research in cognitive psychology and digital‑media literacy.

    If you have any questions, reach out to **aw3088@columbia.edu**.
    """)

# ───────────────────────── main flow
st.title("🧠 Truth Perception Study" if VARIANT=="A" else "✨ Trivia & Feelings Survey")
if ss.get("show_instructions", True): show_instructions()
elif ss.index < len(ss.stimuli): run_trial(ss.stimuli[ss.index], ss.index+1, len(ss.stimuli))
else: finish()
