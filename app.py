from __future__ import annotations

import io
import math
from pathlib import Path
from datetime import datetime

import pandas as pd
import streamlit as st


# ============================================================
# PAGE
# ============================================================
st.set_page_config(
    page_title="Stage 2B — Concept-to-Palette Annotation",
    page_icon="🎨",
    layout="wide",
)

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"
OUTPUT_DIR = HERE / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PALETTE_FILE = DATA_DIR / "palette_448.csv"
CONCEPT_FILE = DATA_DIR / "stage2b_concepts_50.csv"

FAMILIES = [
    "Neutral", "Red", "Orange", "Yellow", "Green",
    "Cyan", "Blue", "Purple", "Pink", "Brown",
]

CONCEPT_GUIDES = {'fire': 'A burning phenomenon characterized by flames, heat, glowing material, and intense visual energy.', 'cherry blossoms': 'Delicate flowering blossoms that appear on cherry trees during spring, often associated with softness, freshness, and seasonal beauty.', 'charcoal': 'A dark carbon-rich material produced from burned wood, associated with a dry, matte, mineral-like appearance.', 'coffee': 'A roasted beverage and natural product associated with coffee beans, brewed liquid, warmth, and rich earthy appearance.', 'emerald gemstones': 'Precious gemstones known for a vivid jewel-like appearance, clarity, depth, and luxurious visual character.', 'honey': 'A thick natural substance produced by bees, associated with warmth, translucency, sweetness, and a rich glowing appearance.', 'mint leaves': 'Fresh aromatic plant leaves associated with coolness, freshness, natural vegetation, and a clean botanical appearance.', 'peacock': 'A bird known for its decorative plumage, iridescent feathers, and visually rich ornamental appearance.', 'roses': 'Decorative flowering plants associated with layered petals, softness, romance, and natural floral beauty.', 'watermelon': 'A fresh fruit with a contrasting outer rind and juicy interior, associated with summer, freshness, and vivid natural appearance.', 'Arctic sea': 'A cold polar ocean environment associated with ice, water, sea surfaces, and a low-temperature atmosphere.', 'beach sand': 'Fine natural material found along coastlines, associated with dry shorelines, sunlight, and warm coastal environments.', 'coral reef': 'A lively underwater marine environment made up of coral formations, aquatic plants, and diverse sea life.', 'desert dunes': 'Large wind-shaped formations of sand found in dry desert environments, associated with heat, open landscapes, and natural earth surfaces.', 'forest': 'A dense natural landscape dominated by trees, vegetation, shaded areas, and layered woodland scenery.', 'green fields': 'Open agricultural or natural land covered with grass or vegetation, associated with freshness, growth, and expansive outdoor scenery.', 'lavender fields': 'Large cultivated landscapes filled with lavender plants, associated with floral rows, open countryside, and soft seasonal scenery.', 'ocean': 'A large natural body of salt water associated with depth, open horizons, waves, and changing atmospheric conditions.', 'sandy beach': 'A coastal environment where sand meets the sea, associated with open shorelines, sunlight, water, and relaxed outdoor scenery.', 'volcanic lava': 'Hot molten rock released during volcanic activity, associated with heat, glowing surfaces, dark rock, and intense natural energy.', 'autumn leaves': 'Tree leaves during the autumn season as vegetation changes before winter, associated with dryness, seasonal transition, and natural variation.', 'clear night sky': 'An unobstructed nighttime sky with minimal cloud cover, often associated with darkness, distant stars, and a calm open atmosphere.', 'cloudy sky': 'A sky covered partly or fully by clouds, creating a soft, diffused, and subdued atmospheric appearance.', 'fresh snow': 'Recently fallen snow covering natural or built surfaces, associated with winter, coldness, softness, and clean outdoor scenery.', 'moonlight': 'Soft illumination of outdoor scenes at night caused by light reflected from the moon.', 'morning fog': 'Low atmospheric mist appearing in the early morning, reducing visibility and creating a soft, muted, and diffused landscape.', 'spring rain': 'Rainfall occurring during spring, associated with wet surfaces, fresh vegetation, soft weather, and seasonal renewal.', 'storm': 'An intense weather condition involving dark atmospheric changes, wind, rain, clouds, and dramatic environmental energy.', 'sunset': 'The period when the sun approaches or moves below the horizon, creating a gradual transition from daylight toward evening.', 'twilight': 'The dim atmospheric period between daylight and night, when the sun is below or near the horizon and the sky gradually transitions into darkness.', 'dramatic': 'A visual mood associated with strong contrast, intensity, emotional impact, and a bold or theatrical atmosphere.', 'dreamy': 'A soft imaginative mood associated with fantasy, gentle atmosphere, visual lightness, and a sense of unreality.', 'earthy': 'A natural visual mood associated with soil, wood, stone, plants, minerals, and grounded organic materials.', 'elegant': 'A refined visual mood associated with sophistication, balance, restraint, polished appearance, and graceful design.', 'energetic': 'A lively visual mood associated with movement, intensity, activity, excitement, and strong visual presence.', 'futuristic': 'A visual concept associated with advanced technology, innovation, science fiction, and imagined future environments.', 'luxurious': 'A premium visual mood associated with richness, refinement, high-quality materials, exclusivity, and sophisticated design.', 'melancholic': 'A subdued emotional mood associated with reflection, sadness, quietness, softness, and restrained atmosphere.', 'mysterious': 'An uncertain or enigmatic visual mood associated with concealment, darkness, ambiguity, depth, and curiosity.', 'playful': 'A cheerful and expressive visual mood associated with fun, experimentation, youthfulness, and lively design.', 'candlelit room': 'An indoor environment illuminated primarily by candles, creating soft localized light, shadows, warmth, and an intimate atmosphere.', 'desert sunset': 'A desert landscape during sunset, combining dry open terrain with the atmospheric transition from daylight toward evening.', 'foggy mountain landscape': 'A mountainous natural environment partly obscured by fog, creating reduced visibility, soft depth, and a muted atmospheric appearance.', 'misty forest': 'A woodland landscape partially covered by mist or fog, creating a soft, muted, and atmospheric appearance.', 'moonlit ocean': 'An ocean scene at night illuminated by reflected moonlight, combining dark water, night atmosphere, and soft natural illumination.', 'moonlit snowy field': 'A snow-covered open landscape at night illuminated by reflected moonlight, combining cold terrain with soft nighttime illumination.', 'rainy autumn afternoon': 'An autumn outdoor scene during rainfall in the afternoon, combining seasonal vegetation, wet surfaces, cloud cover, and subdued daylight.', 'rainy city at night': 'An urban nighttime environment during rainfall, with wet surfaces, artificial lighting, reflections, and a dark atmospheric setting.', 'snowy pine forest': 'A woodland dominated by pine trees covered partly or fully with snow, associated with winter, cold air, vegetation, and layered natural scenery.', 'volcanic landscape at dusk': 'A volcanic terrain during the transition from daylight toward night, combining dark rock, dramatic landforms, and changing atmospheric light.'}


# ============================================================
# FAMILY ASSIGNMENT
# These are navigation aids only, NOT gold labels.
# ============================================================
def assign_family(row):
    L = float(row["L"])
    a = float(row["a"])
    b = float(row["b"])

    if "chroma" in row and pd.notna(row["chroma"]):
        C = float(row["chroma"])
    else:
        C = math.sqrt(a * a + b * b)

    if "hue_angle_deg" in row and pd.notna(row["hue_angle_deg"]):
        h = float(row["hue_angle_deg"])
    else:
        h = math.degrees(math.atan2(b, a)) % 360.0

    if "is_neutral" in row:
        val = row["is_neutral"]
        if isinstance(val, str):
            is_neutral = val.strip().lower() in ["true", "1", "yes"]
        else:
            is_neutral = bool(val)
    else:
        is_neutral = C < 8

    if is_neutral or C < 8:
        return "Neutral"

    if 20 <= h < 90 and L < 58 and b > 8:
        return "Brown"

    if (h >= 330 or h < 15) and L >= 55:
        return "Pink"

    if 300 <= h < 330 and L >= 50:
        return "Pink"

    if h >= 345 or h < 20:
        return "Red"
    if 20 <= h < 55:
        return "Orange"
    if 55 <= h < 100:
        return "Yellow"
    if 100 <= h < 165:
        return "Green"
    if 165 <= h < 210:
        return "Cyan"
    if 210 <= h < 275:
        return "Blue"
    if 275 <= h < 345:
        return "Purple"

    return "Neutral"


# ============================================================
# LOAD / VALIDATE DATA
# ============================================================
@st.cache_data
def load_data():
    palette = pd.read_csv(PALETTE_FILE)
    concepts = pd.read_csv(CONCEPT_FILE)

    required_palette = {
        "palette_index", "L", "a", "b", "R", "G", "B", "HEX"
    }
    required_concepts = {"concept_id", "concept", "category"}

    missing_palette = required_palette - set(palette.columns)
    missing_concepts = required_concepts - set(concepts.columns)

    if missing_palette:
        raise ValueError(f"Palette missing columns: {sorted(missing_palette)}")
    if missing_concepts:
        raise ValueError(f"Concept file missing columns: {sorted(missing_concepts)}")
    if len(palette) != 448:
        raise ValueError(f"Expected 448 palette rows; found {len(palette)}")
    if len(concepts) != 50:
        raise ValueError(f"Expected 50 concepts; found {len(concepts)}")

    palette = palette.copy()
    palette["palette_index"] = palette["palette_index"].astype(int)
    palette["palette_id"] = palette["palette_index"].map(lambda x: f"P{x:03d}")
    palette["family"] = palette.apply(assign_family, axis=1)
    palette = palette.sort_values("palette_index").reset_index(drop=True)
    concepts = concepts.reset_index(drop=True)
    return palette, concepts


palette, concepts = load_data()


# ============================================================
# HELPERS
# ============================================================
OUTPUT_FIELDS = [
    "rater_id",
    "concept_id",
    "concept",
    "category",
    "concept_guide",
    "selected_families",
    "primary_colour",
    "secondary_colour",
    "tertiary_colour",
    "no_suitable_colour",
    "viewed_full_palette",
    "annotation_timestamp",
]


def csv_bytes(annotations: dict) -> bytes:
    rows = []
    for _, concept_row in concepts.iterrows():
        cid = str(concept_row["concept_id"])
        if cid in annotations:
            rows.append(annotations[cid])
    if not rows:
        df = pd.DataFrame(columns=OUTPUT_FIELDS)
    else:
        df = pd.DataFrame(rows)
        for col in OUTPUT_FIELDS:
            if col not in df.columns:
                df[col] = ""
        df = df[OUTPUT_FIELDS]
    return df.to_csv(index=False).encode("utf-8")


def load_annotation_csv(uploaded, expected_rater: str):
    old = pd.read_csv(uploaded, dtype=str).fillna("")
    needed = {"concept_id", "rater_id"}
    if not needed.issubset(old.columns):
        raise ValueError("This does not look like a Stage 2B annotation CSV.")

    rater_values = set(old["rater_id"].astype(str).str.strip())
    rater_values.discard("")
    if rater_values and rater_values != {expected_rater}:
        raise ValueError(
            f"Uploaded file belongs to {sorted(rater_values)}; "
            f"current session is {expected_rater}."
        )

    anns = {}
    valid_ids = set(concepts["concept_id"].astype(str))
    for _, row in old.iterrows():
        cid = str(row["concept_id"])
        if cid in valid_ids:
            anns[cid] = row.to_dict()
    return anns


def save_server_copy(rater_id: str, annotations: dict):
    # Convenience backup only. Streamlit Community Cloud storage can reset,
    # so the rater should still download the CSV before leaving.
    path = OUTPUT_DIR / f"{rater_id}_annotations.csv"
    path.write_bytes(csv_bytes(annotations))


def first_unfinished_index(annotations: dict):
    for i, row in concepts.iterrows():
        if str(row["concept_id"]) not in annotations:
            return int(i)
    return 0


def reset_concept_widget_state():
    # Remove only per-concept widget keys.
    prefixes = (
        "family_", "swatch_", "no_suitable_", "view_all_", "selected_ids_"
    )
    for key in list(st.session_state.keys()):
        if str(key).startswith(prefixes):
            del st.session_state[key]


# ============================================================
# SESSION INITIALIZATION
# ============================================================
defaults = {
    "started": False,
    "rater_id": None,
    "annotations": {},
    "current_idx": 0,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ============================================================
# CSS
# ============================================================
st.markdown(
    """
    <style>
    .main .block-container {
        max-width: 1250px;
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }
    .concept-title {
        text-align:center;
        font-size:2rem;
        font-weight:700;
        margin:0.2rem 0 0.1rem 0;
    }
    .concept-meta {
        text-align:center;
        color:#666;
        margin-bottom:0.8rem;
    }
    .guide-box {
        background:#f7f7f8;
        border:1px solid #d8d8dc;
        border-radius:10px;
        padding:14px 16px;
        margin-bottom:0.4rem;
    }
    .swatch {
        height:74px;
        border-radius:8px;
        border:2px solid rgba(0,0,0,.18);
        display:flex;
        align-items:flex-end;
        justify-content:center;
        padding:5px;
        margin-top:4px;
        font-weight:700;
        text-shadow:0 0 3px rgba(255,255,255,.75);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# START / RESUME SCREEN
# ============================================================
if not st.session_state.started:
    st.title("🎨 Stage 2B — Concept-to-Palette Human Annotation")

    st.info(
        "For each concept, select 1–3 colours from the fixed women’s-apparel "
        "fashion palette that best represent the concept as colour inspiration."
    )

    st.markdown(
        """
        **Annotation rules**
        - Work independently.
        - Do not consult another rater's selections.
        - Do not use LLM or CLIP predictions.
        - Use the short concept guide only to understand the concept.
        - Select 1 colour if one is enough; select 2–3 only when multiple colours are important.
        - The broad colour families are only navigation aids. Your actual answer is the selected palette ID(s).
        """
    )

    rater_label = st.selectbox(
        "Select your assigned rater ID",
        ["Rater 1", "Rater 2", "Rater 3", "Rater 4", "Rater 5"],
        index=1,
        help="Use only the rater number assigned by the researcher.",
    )
    rater_id = rater_label.lower().replace(" ", "")

    resume_file = st.file_uploader(
        "Optional: upload your previous progress CSV to resume",
        type=["csv"],
        help="Use this only if you previously downloaded your own progress file.",
    )

    col_a, col_b = st.columns([1, 3])
    with col_a:
        start = st.button("Start / Resume", type="primary", use_container_width=True)

    if start:
        annotations = {}

        if resume_file is not None:
            try:
                annotations = load_annotation_csv(resume_file, rater_id)
            except Exception as e:
                st.error(str(e))
                st.stop()
        else:
            # Try a temporary server-side copy if the cloud instance still has it.
            server_path = OUTPUT_DIR / f"{rater_id}_annotations.csv"
            if server_path.exists() and server_path.stat().st_size > 0:
                try:
                    with server_path.open("rb") as f:
                        annotations = load_annotation_csv(f, rater_id)
                except Exception:
                    annotations = {}

        st.session_state.rater_id = rater_id
        st.session_state.annotations = annotations
        st.session_state.current_idx = first_unfinished_index(annotations)
        st.session_state.started = True
        reset_concept_widget_state()
        st.rerun()

    st.warning(
        "Important: Streamlit Community Cloud storage is not guaranteed to be "
        "permanent. Download your progress CSV before closing the browser. "
        "You can upload it later to resume."
    )
    st.stop()


# ============================================================
# ACTIVE ANNOTATION
# ============================================================
rater_id = st.session_state.rater_id
annotations = st.session_state.annotations
idx = int(st.session_state.current_idx)
row = concepts.iloc[idx]

cid = str(row["concept_id"])
concept = str(row["concept"])
category = str(row["category"])
guide = CONCEPT_GUIDES.get(
    concept,
    "Interpret the concept according to its usual meaning and select the "
    "palette colours that best represent it as colour inspiration for women's apparel."
)

completed_count = len(annotations)

top1, top2 = st.columns([3, 1])
with top1:
    st.progress(completed_count / len(concepts))
    st.caption(
        f"Completed {completed_count} / {len(concepts)} concepts "
        f"• Current concept {idx + 1} / {len(concepts)}"
    )
with top2:
    st.markdown(f"**Rater:** `{rater_id}`")

st.markdown(f'<div class="concept-title">{concept.upper()}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="concept-meta">Sampling stratum: {category}</div>', unsafe_allow_html=True)

st.markdown(
    f'<div class="guide-box"><b>Concept guide</b><br>{guide}</div>',
    unsafe_allow_html=True
)
st.caption(
    "Use this description only to understand the concept. Choose colours according "
    "to your own semantic interpretation in a women’s-fashion context."
)

# Restore saved values into defaults when visiting an already-annotated item.
saved = annotations.get(cid, {})

family_key = f"selected_ids_{cid}_families"
if family_key not in st.session_state:
    saved_fams = [
        x for x in str(saved.get("selected_families", "")).split(";") if x
    ]
    st.session_state[family_key] = saved_fams

families = st.multiselect(
    "Choose one or more broad colour families to browse",
    FAMILIES,
    default=st.session_state[family_key],
    key=f"family_{cid}",
)

view_all_default = str(saved.get("viewed_full_palette", "")).lower() == "true"
view_all = st.checkbox(
    "View all 448 colours",
    value=view_all_default,
    key=f"view_all_{cid}",
)

no_suitable_default = str(saved.get("no_suitable_colour", "")).lower() == "true"
no_suitable = st.checkbox(
    "No suitable palette colour",
    value=no_suitable_default,
    key=f"no_suitable_{cid}",
)

saved_selected = [
    str(saved.get(k, "")).strip()
    for k in ["primary_colour", "secondary_colour", "tertiary_colour"]
    if str(saved.get(k, "")).strip()
]
selection_state_key = f"selected_ids_{cid}"
if selection_state_key not in st.session_state:
    st.session_state[selection_state_key] = saved_selected

if no_suitable:
    st.session_state[selection_state_key] = []

if view_all:
    visible = palette
    visible_title = "All 448 palette colours"
elif families:
    visible = palette[palette["family"].isin(families)]
    visible_title = " / ".join(families)
else:
    visible = palette.iloc[0:0]
    visible_title = ""

if visible.empty and not view_all and not families:
    st.info(
        "Choose one or more colour families above, or select "
        "“View all 448 colours”."
    )
else:
    st.markdown(f"#### {visible_title} — {len(visible)} colours")

    # Render in groups of 7. Each swatch has an exact HEX preview and a checkbox.
    rows_list = list(visible.to_dict("records"))
    for start_i in range(0, len(rows_list), 7):
        cols = st.columns(7)
        for j, sw in enumerate(rows_list[start_i:start_i + 7]):
            pid = sw["palette_id"]
            hexv = str(sw["HEX"])
            checked = pid in st.session_state[selection_state_key]
            with cols[j]:
                st.markdown(
                    f'<div class="swatch" style="background:{hexv};">{pid}</div>',
                    unsafe_allow_html=True
                )
                choice = st.checkbox(
                    "Select",
                    value=checked,
                    key=f"swatch_{cid}_{pid}",
                    disabled=no_suitable,
                )

                selected_now = st.session_state[selection_state_key]
                if choice and pid not in selected_now:
                    selected_now.append(pid)
                elif (not choice) and pid in selected_now:
                    selected_now.remove(pid)

# Remove duplicates while preserving order.
seen = set()
selected_ids = []
for pid in st.session_state[selection_state_key]:
    if pid not in seen:
        selected_ids.append(pid)
        seen.add(pid)
st.session_state[selection_state_key] = selected_ids

if len(selected_ids) > 3:
    st.error(
        f"You currently selected {len(selected_ids)} colours. "
        "Please reduce the selection to at most 3."
    )
elif selected_ids:
    st.success(
        "Current ranked selection: " +
        " → ".join(f"{i+1}: {p}" for i, p in enumerate(selected_ids))
    )
elif not no_suitable:
    st.caption("No palette colour selected yet.")

st.caption(
    "The order in which colours are first selected is saved as "
    "primary → secondary → tertiary."
)


# ============================================================
# SAVE / NAVIGATION
# ============================================================
def save_current():
    selected = list(st.session_state[selection_state_key])

    if no_suitable:
        selected = []
    else:
        if not selected:
            st.error("Select 1–3 palette colours, or choose “No suitable palette colour”.")
            return False
        if len(selected) > 3:
            st.error("Select at most three palette colours.")
            return False
        if not families and not view_all:
            st.error("Choose at least one family or view the full palette.")
            return False

    colours = selected + ["", "", ""]
    annotation = {
        "rater_id": rater_id,
        "concept_id": cid,
        "concept": concept,
        "category": category,
        "concept_guide": guide,
        "selected_families": ";".join(sorted(families)),
        "primary_colour": colours[0],
        "secondary_colour": colours[1],
        "tertiary_colour": colours[2],
        "no_suitable_colour": str(bool(no_suitable)),
        "viewed_full_palette": str(bool(view_all)),
        "annotation_timestamp": datetime.now().isoformat(timespec="seconds"),
    }
    st.session_state.annotations[cid] = annotation
    save_server_copy(rater_id, st.session_state.annotations)
    return True


nav1, nav2, nav3 = st.columns([1, 1, 2])

with nav1:
    if st.button("← Previous", use_container_width=True, disabled=(idx <= 0)):
        st.session_state.current_idx = idx - 1
        reset_concept_widget_state()
        st.rerun()

with nav2:
    if st.button("Save & Next →", type="primary", use_container_width=True):
        if save_current():
            if idx >= len(concepts) - 1:
                st.success("All concepts reached. Download the final CSV below.")
            else:
                st.session_state.current_idx = idx + 1
                reset_concept_widget_state()
                st.rerun()

with nav3:
    progress_bytes = csv_bytes(st.session_state.annotations)
    st.download_button(
        "⬇ Download current progress CSV",
        data=progress_bytes,
        file_name=f"{rater_id}_annotations.csv",
        mime="text/csv",
        use_container_width=True,
    )

# Completion panel
if len(st.session_state.annotations) == len(concepts):
    st.divider()
    st.success(
        "Annotation complete: 50 / 50 concepts saved. "
        "Please download the final CSV and send it to the researcher."
    )
    st.download_button(
        "⬇ Download FINAL annotation CSV",
        data=csv_bytes(st.session_state.annotations),
        file_name=f"{rater_id}_annotations.csv",
        mime="text/csv",
        type="primary",
        use_container_width=True,
    )

with st.expander("Session / safety information"):
    st.write(
        "Each rater must work independently. Do not inspect other raters' files. "
        "Do not use LLM or CLIP predictions during human annotation."
    )
    st.write(
        "The app creates a temporary server-side backup, but Streamlit Community "
        "Cloud can restart. The downloaded CSV is the authoritative copy."
    )
