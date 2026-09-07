import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Student Statistics Dashboard", page_icon="📊", layout="wide"
)

st.title("📊 Student Statistics & Filter Dashboard")

# 1. फ़ाइल लोड करने का ऑटोमैटिक सिस्टम
uploaded_file = st.sidebar.file_uploader(
    "नई Excel फ़ाइल अपलोड करें (Optional)", type=["xlsx", "xls"]
)

# फ़ोल्डर में मौजूद संभावित एक्सेल फाइलें चेक करें
default_files = [
    "Class XI C, 2026-27_2.xlsx",
    "Class XI C, 2026-27.xlsx",
]
selected_default = None
for f in default_files:
  if os.path.exists(f):
    selected_default = f
    break

target_file = (
    uploaded_file
    if uploaded_file
    else (selected_default if selected_default else "Class XI C, 2026-27_2.xlsx")
)


def detect_gender(name):
  """अगर फाइल में Gender कॉलम न हो तो नाम से पहचानें"""
  name = str(name).upper().strip()
  female_keywords = [
      "KUMARI",
      "DEVI",
      "KHATOON",
      "KHATUN",
      "PARAVIN",
      "BEGUM",
      "ANANYA",
      "ANCHAL",
      "ANJALI",
      "ARCHANA",
      "ARPITA",
      "AYUSHI",
      "CHANDNI",
      "DIVYA",
      "GUNGUN",
      "HARSHITA",
      "JYOTI",
      "KAJAL",
      "KANISHKA",
      "KAYNAT",
      "KHUSHBOO",
      "KRITI",
      "MANISHA",
      "MEENAKSHI",
      "NAZREENA",
      "NEELAM",
      "PAYAL",
      "PREETI",
      "PREMLATA",
      "PRIYA",
      "PRIYANSHI",
      "RAGINI",
      "REETA",
      "RIYA",
      "RUKSAR",
      "SABA",
      "SAGUFTA",
      "SAINA",
      "SALONI",
      "SANIYA",
      "SAPANA",
      "SARASWATI",
      "SARITA",
      "SEWANTI",
      "SHABANA",
      "SHEETAL",
      "SHIVANGI",
      "SHREYA",
      "SHWETA",
      "SMRITI",
      "SNEHA",
      "SUNITA",
      "SUSHMITA",
      "YASMIN",
      "AKSA",
  ]
  for kw in female_keywords:
    if kw in name:
      return "Girl"
  return "Boy"


@st.cache_data
def load_data(file_source):
  df = pd.read_excel(file_source)
  df.columns = df.columns.astype(str).str.strip()

  # Category क्लीनिंग
  cat_cols = [c for c in df.columns if c.upper() in ["CAT.", "CAT", "CATEGORY"]]
  cat_col = cat_cols[0] if cat_cols else None
  if cat_col:
    df["CAT_CLEAN"] = (
        df[cat_col].astype(str).str.strip().str.upper().replace("NAN", "-")
    )
  else:
    df["CAT_CLEAN"] = "-"

  # Occupation क्लीनिंग (HE / HS / OTH)
  occ_cols = [c for c in df.columns if "OCCUPATION" in c.upper()]
  occ_col = occ_cols[0] if occ_cols else None
  if occ_col:
    df["OCCUPATION_CLEAN"] = (
        df[occ_col].astype(str).str.strip().str.upper().replace("NAN", "-")
    )
  else:
    df["OCCUPATION_CLEAN"] = "-"

  # Gender क्लीनिंग (Boy / Girl)
  gender_cols = [c for c in df.columns if c.upper() in ["GENDER", "SEX"]]
  if gender_cols:
    df["GENDER_CLEAN"] = (
        df[gender_cols[0]]
        .astype(str)
        .str.strip()
        .str.capitalize()
        .replace({"M": "Boy", "F": "Girl", "Male": "Boy", "Female": "Girl"})
    )
  elif "STUDENT'S NAME" in df.columns:
    df["GENDER_CLEAN"] = df["STUDENT'S NAME"].apply(detect_gender)
  else:
    df["GENDER_CLEAN"] = "Not Available"

  return df, occ_col


try:
  df, original_occ_col = load_data(target_file)

  st.sidebar.header("🔍 फ़िल्टर (Filters)")

  # 1. Gender Dropdown (Boy / Girl)
  gender_options = ["All"] + sorted(
      [x for x in df["GENDER_CLEAN"].unique() if x != "-"]
  )
  selected_gender = st.sidebar.selectbox("Gender:", gender_options)

  # 2. Category Dropdown (GEN / OBC / SC / ST)
  cat_options = ["All"] + sorted(
      [x for x in df["CAT_CLEAN"].unique() if x != "-"]
  )
  selected_cat = st.sidebar.selectbox("Category (CAT.):", cat_options)

  # 3. Occupation Dropdown (HE / HS / OTH)
  occ_options = ["All"] + sorted(
      [x for x in df["OCCUPATION_CLEAN"].unique() if x != "-"]
  )
  selected_occ = st.sidebar.selectbox("Occupation (HE/HS/OTH):", occ_options)

  # डेटा फ़िल्टरिंग
  filtered_df = df.copy()
  if selected_gender != "All":
    filtered_df = filtered_df[filtered_df["GENDER_CLEAN"] == selected_gender]
  if selected_cat != "All":
    filtered_df = filtered_df[filtered_df["CAT_CLEAN"] == selected_cat]
  if selected_occ != "All":
    filtered_df = filtered_df[filtered_df["OCCUPATION_CLEAN"] == selected_occ]

  # मुख्य स्टेटिस्टिक्स कार्ड्स
  col1, col2, col3, col4, col5 = st.columns(5)
  col1.metric("कुल छात्र (Total)", len(df))
  col2.metric("फ़िल्टर छात्र (Filtered)", len(filtered_df))
  col3.metric("Gender", selected_gender)
  col4.metric("Category", selected_cat)
  col5.metric("Occupation", selected_occ)

  st.divider()

  # सांख्यिकी ब्रेकडाउन (Statistics Breakdown)
  st.subheader("📈 सांख्यिकी सारांश (Statistics Breakdown)")
  stat_col1, stat_col2, stat_col3 = st.columns(3)

  with stat_col1:
    st.write("**👦/👧 Gender वार संख्या:**")
    st.dataframe(
        df["GENDER_CLEAN"]
        .value_counts()
        .rename_axis("Gender")
        .reset_index(name="छात्र संख्या")
    )

  with stat_col2:
    st.write("**🏷️ Category वार संख्या:**")
    st.dataframe(
        df["CAT_CLEAN"].value_counts().rename_axis("Category").reset_index(
            name="छात्र संख्या"
        )
    )

  with stat_col3:
    st.write("**🏭 Occupation वार संख्या:**")
    st.dataframe(
        df["OCCUPATION_CLEAN"]
        .value_counts()
        .rename_axis("Occupation")
        .reset_index(name="छात्र संख्या")
    )

  st.divider()

  # फ़िल्टर किया हुआ डेटा टेबल
  st.subheader(f"📋 छात्र विवरण तालिका ({len(filtered_df)} रिकॉर्ड मिले)")
  display_cols = [
      "ROLL. NO",
      "STUDENT'S NAME",
      "GENDER_CLEAN",
      "FATHER'S NAME",
      "CAT.",
      original_occ_col,
      "MOB. NO.",
      "ADDRESS ",
  ]
  available_cols = [c for c in display_cols if c in filtered_df.columns]

  st.dataframe(
      filtered_df[available_cols].rename(columns={"GENDER_CLEAN": "GENDER"}),
      use_container_width=True,
  )

  # CSV डाउनलोड
  csv_data = filtered_df.to_csv(index=False).encode("utf-8")
  st.download_button(
      label="📥 फ़िल्टर डेटा डाउनलोड करें (CSV)",
      data=csv_data,
      file_name="filtered_students_data.csv",
      mime="text/csv",
  )

except Exception as e:
  st.error(
      f"फ़ाइल लोड करने में त्रुटि: कृपया फ़ाइल का नाम और पाथ जांचें या साइडबार से फ़ाइल अपलोड करें। ({e})"
  )
