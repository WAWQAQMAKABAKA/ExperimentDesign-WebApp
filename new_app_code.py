from __future__ import annotations

import json
import random
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Final

import pandas as pd
import streamlit as st

# ══════════════════════════════════════ PATH & CONFIG ══════════════════════════════════════
BASE:     Final = Path(__file__).parent
STIM:     Final = BASE / "stimuli.json"
IMGS:     Final = BASE / "images"
LOGS:     Final = BASE / "logs"; LOGS.mkdir(exist_ok=True)
LOG_CSV:  Final = LOGS / "responses.csv"

N_TRUE:       Final = 8
N_FALSE:      Final = 8
N_PHOTO_EACH: Final = 4

SA_JSON = st.secrets.get("GSPREAD_KEY")   # optional Google Sheets
GA_ID   = st.secrets.get("GA_ID", {}).get("value", "")  # optional GA4

# ══════════════════════════════════════ GOOGLE SHEETS ══════════════════════════════════════
if SA_JSON:
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials

    _SCOPE = (
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    )
    _CREDS = ServiceAccountCredentials.from_json_keyfile_dict(SA_JSON, _SCOPE)
    _WS    = gspread.authorize(_CREDS).open("Trivia_Responses").worksheet("Responses")

    def to_sheet(df: pd.DataFrame) -> None:
        _WS.append_rows(df.astype(str).values.tolist())
else:
    def to_sheet(_: pd.DataFrame) -> None: ...

# ══════════════════════════════════════ MODEL ══════════════════════════════════════════════
@dataclass
class Stimulus:
    id: str
    text: str
    truth: bool
    photo: str | None
    show_photo: bool = False

    @property
    def path(self) -> Path | None:
        return IMGS / self.photo if self.photo and self.photo.endswith(".png") else None


def load_bank() -> List[Stimulus]:
    return [Stimulus(**d) for d in json.loads(STIM.read_text())]


def balanced_subset(bank: List[Stimulus]) -> List[Stimulus]:
    true = random.sample([b for b in bank if b.truth], N_TRUE)
    false = random.sample([b for b in bank if not b.truth], N_FALSE)
    trials = true + false
    random.shuffle(trials)

    with_ph = [s for s in trials if s.path]; random.shuffle(with_ph)
    t = f = 0
    for s in with_ph:
        if s.truth and t < N_PHOTO_EACH:
            s.show_photo, t = True, t + 1
        elif not s.truth and f < N_PHOTO_EACH:
            s.show_photo, f = True, f + 1
        if t == f == N_PHOTO_EACH:
            break
    return trials


# ══════════════════════════════════════ STREAMLIT INIT ═════════════════════════════════════
st.set_page_config("Truth Perception Study", "🤔", "centered")

# clean use of new query API
st.query_params.setdefault("variant", random.choice(("A", "B")))
VARIANT: Final = st.query_params["variant"]
BTN_CFG = {"type": "primary", "use_container_width": VARIANT == "B"}

if GA_ID:
    st.markdown(
        f"""
        <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
        <script>window.dataLayer=window.dataLayer||[];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js',new Date()); gtag('config','{GA_ID}');</script>
        """,
        unsafe_allow_html=True,
    )

# ══════════════════════════════════════ STATE ══════════════════════════════════════════════
ss = st.session_state
ss.setdefault("pid", str(uuid.uuid4()))
ss.setdefault("group", random.choice(("Explain", "Emotion")))
ss.setdefault("stimuli", balanced_subset(load_bank()))
ss.setdefault("idx", 0)
ss.setdefault("log", [])
ss.setdefault("clock", 0.0)

# ══════════════════════════════════════ HELPERS ════════════════════════════════════════════
def header() -> None:
    st.title("🧠 Truth Perception Study" if VARIANT == "A" else "✨ Trivia & Feelings Survey")


def instruction_page() -> None:
    st.markdown("### Instructions")
    st.info(
        "Decide **True/False** for each statement, then "
        + ("briefly explain your choice." if ss.group == "Explain" else "describe how it makes you feel.")
    )
    if st.button("Start", **BTN_CFG):
        ss.show_instruct = False
        st.rerun()


def trial_page(stim: Stimulus, idx: int, total: int) -> None:
    st.subheader(f"Statement {idx}/{total}")
    st.write(stim.text)
    if stim.show_photo and stim.path and stim.path.exists():
        st.image(stim.path.read_bytes(), width=320)

    if not ss.clock:
        ss.clock = time.time()

    with st.form(f"form_{stim.id}"):
        answer = st.radio("Is it…", ("True", "False"), horizontal=True)
        prompt = "Explain:" if ss.group == "Explain" else "Feelings:"
        memo = st.text_area(prompt, height=120)
        ok = st.form_submit_button("Submit & Next", **BTN_CFG)

    if ok:
        if not memo.strip():
            st.warning("Text cannot be empty."); st.stop()
        rt = round(time.time() - ss.clock, 2)
        ss.clock = 0.0
        ss.log.append(
            dict(
                timestamp=datetime.utcnow().isoformat(),
                pid=ss.pid,
                variant=VARIANT,
                prompt_group=ss.group,
                stim_id=stim.id,
                truth=stim.truth,
                answer=answer == "True",
                correct=(answer == "True") == stim.truth,
                response=memo.strip(),
                photo=stim.show_photo,
                rt=rt,
                py=sys.version.split()[0],
                os=platform.platform(),
                streamlit=st.__version__,
            )
        )
        ss.idx += 1
        st.rerun()


def debrief_page() -> None:
    st.balloons()
    st.success("✔️ Responses saved — thank you!")
    df = pd.DataFrame(ss.log)
    df = pd.concat([pd.read_csv(LOG_CSV), df], ignore_index=True) if LOG_CSV.exists() else df
    df.to_csv(LOG_CSV, index=False)
    save_to_gsheet(df)

    st.markdown("### Session stats"); st.dataframe(df[["stim_id", "correct", "rt"]])

    st.markdown("### Debriefing")
    st.write(
        """
        This experiment examines how **visual cues** and **reasoning style**
        influence truth‑judgements. Your anonymous data aid research on digital
        misinformation. Questions? aw3088@columbia.edu
        """
    )


# ══════════════════════════════════════ ROUTER ═════════════════════════════════════════════
header()
if ss.get("show_instruct", True):
    instruction_page()
elif ss.idx < len(ss.stimuli):
    trial_page(ss.stimuli[ss.idx], ss.idx + 1, len(ss.stimuli))
else:
    debrief_page()
