STAGE 2B STREAMLIT DEPLOYMENT PACKAGE
====================================

Files included
--------------
app.py
requirements.txt
data/palette_448.csv
data/stage2b_concepts_50.csv
.streamlit/config.toml
outputs/.gitkeep

Purpose
-------
Online human annotation for Stage 2B concept-to-palette grounding.
Supports Rater 1 through Rater 5.

IMPORTANT DATA SAFETY
---------------------
Streamlit Community Cloud local storage is not guaranteed to persist forever.
The app therefore provides:
1. temporary server-side saving,
2. "Download current progress CSV", and
3. "Upload previous progress CSV to resume".

Each rater should download their CSV before closing the browser.
The final returned files should be:
rater2_annotations.csv
rater3_annotations.csv
rater4_annotations.csv
rater5_annotations.csv

Rater 1 is already completed and should be kept separately by the researcher.

DEPLOYMENT
----------
1. Create a private or public GitHub repository.
2. Upload the CONTENTS of this folder, keeping the same directory structure.
3. Go to https://share.streamlit.io/
4. Sign in with GitHub.
5. Click "Create app" / "New app".
6. Select the repository and branch (normally main).
7. Main file path: app.py
8. Deploy.
9. Test the generated URL yourself before sending it to raters.

RATER INSTRUCTIONS
------------------
1. Open the Streamlit URL.
2. Select ONLY the assigned Rater ID.
3. Do not inspect another rater's answers.
4. Do not use LLM or CLIP predictions.
5. Complete the 50 concepts independently.
6. Download progress periodically.
7. At 50/50, download the FINAL CSV.
8. Send only that CSV back to the researcher.

Do not rename palette IDs or edit the two data CSV files after annotation begins.
