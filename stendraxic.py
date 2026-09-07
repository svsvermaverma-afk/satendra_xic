import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Student Data Dashboard", page_icon="📊", layout="wide"
)

st.title("📊 Student Statistics & Filter Dashboard")

# Excel फ़ाइल लोड करें
uploaded_file = st.sidebar.file_uploader(
    "Excel फ़ाइल अपलोड करें (वैकल्पिक)", type=["xlsx", "xls"]
)
file_path = uploaded_file if uploaded_file else "Class XI C, 2026-27.xlsx"


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
def load_data(path):
  df = pd.read_excel(path)
  df.columns = df.columns.str.strip()

  # 1. Occupation क्लीनिंग
  occ_cols = [c for c in df.columns if "OCCUPATION" in c.upper()]
  occ_col = occ_cols[0] if occ_cols else None
  if occ_col:
    df["OCCUPATION_CLEAN"] = (
        df[occ_col].astype(str).str.strip().str.upper().replace("NAN", "-")
    )
  else:
    df["OCCUPATION_CLEAN"] = "-"

  # 2. Category क्लीनिंग
  if "CAT." in df.columns:
    df["CAT_CLEAN"] = (
        df["CAT."].astype(str).str.strip().str.upper().replace("NAN", "-")
    )
  else:
    df["CAT_CLEAN"] = "-"

  # 3. Gender (Boy / Girl) पहचान
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
  df, original_occ_col = load_data(file_path)

  # Sidebar Filters
  st.sidebar.header("🔍 फ़िल्टर (Filters)")

  # Gender Filter (Boy / Girl)
  all_genders = ["All"] + sorted(
      [x for x in df["GENDER_CLEAN"].unique() if x != "-"]
  )
  selected_gender = st.sidebar.selectbox("Gender (Boy/Girl):", all_genders)

  # Category Filter (GEN, OBC, SC, ST)
  all_cats = ["All"] + sorted(
      [x for x in df["CAT_CLEAN"].unique() if x != "-"]
  )
  selected_cat = st.sidebar.selectbox("Category (CAT.):", all_cats)

  # Occupation Filter (HE, HS, OTH)
  all_occupations = ["All"] + sorted(
      [x for x in df["OCCUPATION_CLEAN"].unique() if x != "-"]
  )
  selected_occ = st.sidebar.selectbox("Occupation (HE/HS/OTH):", all_occupations)

  # डेटा फ़िल्टरिंग
  filtered_df = df.copy()
  if selected_gender != "All":
    filtered_df = filtered_df[filtered_df["GENDER_CLEAN"] == selected_gender]
  if selected_cat != "All":
    filtered_df = filtered_df[filtered_df["CAT_CLEAN"] == selected_cat]
  if selected_occ != "All":
    filtered_df = filtered_df[filtered_df["OCCUPATION_CLEAN"] == selected_occ]

  # मुख्य स्टेटिस्टिक्स (Key Metrics)
  col1, col2, col3, col4, col5 = st.columns(5)
  col1.metric("कुल छात्र (Total)", len(df))
  col2.metric("फ़िल्टर छात्र", len(filtered_df))
  col3.metric("चुना गया Gender", selected_gender)
  col4.metric("चुनी गई Category", selected_cat)
  col5.metric("चुना गया Occupation", selected_occ)

  st.divider()

  # सांख्यिकी सारांश (Breakdown Columns)
  st.subheader("📈 सांख्यिकी सारांश (Statistics Breakdown)")
  stat_col1, stat_col2, stat_col3 = st.columns(3)

  with stat_col1:
    st.write("**👦/👧 Gender वार संख्या:**")
    st.dataframe(
        df["GENDER_CLEAN"]
        .value_counts()
        .rename_axis("Gender")
        .reset_index(name="संख्या")
    )

  with stat_col2:
    st.write("**🏷️ Category वार संख्या:**")
    st.dataframe(
        df["CAT_CLEAN"].value_counts().rename_axis("Category").reset_index(
            name="संख्या"
        )
    )

  with stat_col3:
    st.write("**🏭 Occupation वार संख्या:**")
    st.dataframe(
        df["OCCUPATION_CLEAN"]
        .value_counts()
        .rename_axis("Occupation")
        .reset_index(name="संख्या")
    )

  st.divider()

  # फ़िल्टर किया हुआ डेटा टेबल
  st.subheader(f"📋 छात्र विवरण ({len(filtered_df)} छात्र मिले)")
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

  # कॉलम का डिस्प्ले नाम सुंदर करने के लिए
  rename_map = {"GENDER_CLEAN": "GENDER"}
  st.dataframe(
      filtered_df[available_cols].rename(columns=rename_map),
      use_container_width=True,
  )

  # CSV डाउनलोड बटन
  csv_data = filtered_df.to_csv(index=False).encode("utf-8")
  st.download_button(
      label="📥 फ़िल्टर डेटा डाउनलोड करें (CSV)",
      data=csv_data,
      file_name="filtered_students.csv",
      mime="text/csv",
  )

except Exception as e:
  st.error(f"फ़ाइल लोड करने में त्रुटि: {e}")
