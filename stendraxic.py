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


@st.cache_data
def load_data(path):
  df = pd.read_excel(path)
  # कॉलम के खाली स्पेस हटाएं
  df.columns = df.columns.str.strip()

  # Occupation कॉलम का नाम पहचानें
  occ_cols = [c for c in df.columns if "OCCUPATION" in c.upper()]
  occ_col = occ_cols[0] if occ_cols else None

  if occ_col:
    df["OCCUPATION_CLEAN"] = (
        df[occ_col].astype(str).str.strip().str.upper().replace("NAN", "-")
    )
  else:
    df["OCCUPATION_CLEAN"] = "-"

  if "CAT." in df.columns:
    df["CAT_CLEAN"] = (
        df["CAT."].astype(str).str.strip().str.upper().replace("NAN", "-")
    )
  else:
    df["CAT_CLEAN"] = "-"

  return df, occ_col


try:
  df, original_occ_col = load_data(file_path)

  # Sidebar Filters
  st.sidebar.header("🔍 फ़िल्टर (Filters)")

  # Occupation Filter (HE, HS, OTH आदि)
  all_occupations = ["All"] + sorted(
      [x for x in df["OCCUPATION_CLEAN"].unique() if x != "-"]
  )
  selected_occ = st.sidebar.selectbox("Occupation चुनें:", all_occupations)

  # Category Filter (GEN, OBC, SC, ST)
  all_cats = ["All"] + sorted(
      [x for x in df["CAT_CLEAN"].unique() if x != "-"]
  )
  selected_cat = st.sidebar.selectbox("Category (CAT.) चुनें:", all_cats)

  # डेटा फ़िल्टरिंग
  filtered_df = df.copy()
  if selected_occ != "All":
    filtered_df = filtered_df[filtered_df["OCCUPATION_CLEAN"] == selected_occ]
  if selected_cat != "All":
    filtered_df = filtered_df[filtered_df["CAT_CLEAN"] == selected_cat]

  # मुख्य स्टेटिस्टिक्स (Key Metrics)
  col1, col2, col3, col4 = st.columns(4)
  col1.metric("कुल छात्र (Total)", len(df))
  col2.metric("फ़िल्टर किए गए छात्र", len(filtered_df))
  col3.metric("चुनी गई Category", selected_cat)
  col4.metric("चुना गया Occupation", selected_occ)

  st.divider()

  # संक्षिप्त सांख्यिकी चार्ट/टेबल
  st.subheader("📈 Category & Occupation सारांश (Breakdown)")
  stat_col1, stat_col2 = st.columns(2)

  with stat_col1:
    st.write("**Category वार संख्या:**")
    st.dataframe(
        df["CAT_CLEAN"].value_counts().rename_axis("Category").reset_index(
            name="संख्या"
        )
    )

  with stat_col2:
    st.write("**Occupation वार संख्या:**")
    st.dataframe(
        df["OCCUPATION_CLEAN"]
        .value_counts()
        .rename_axis("Occupation")
        .reset_index(name="संख्या")
    )

  st.divider()

  # फ़िल्टर किया हुआ डेटा टेबल
  st.subheader(f"📋 छात्र विवरण ({len(filtered_df)} छात्र मिले)")
  # देखने लायक मुख्य कॉलम
  display_cols = [
      "ROLL. NO",
      "STUDENT'S NAME",
      "FATHER'S NAME",
      "CAT.",
      original_occ_col,
      "MOB. NO.",
      "ADDRESS",
  ]
  available_cols = [c for c in display_cols if c in filtered_df.columns]

  st.dataframe(filtered_df[available_cols], use_container_width=True)

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
