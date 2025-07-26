import streamlit as st
import pandas as pd
import altair as alt

# --- Load the CSV data ---
DATA_PATH = "Suryacore/data/ingredients.csv"
df = pd.read_csv(DATA_PATH)

# --- Backend logic to compute all metrics automatically ---
def calculate_metrics(df, ingredient, sample_size):
    try:
        row = df[df["NAME"].str.lower() == ingredient.lower()].iloc[0]
        
        # Dynamically identify all metric columns except NAME and COST
        metric_columns = [col for col in df.columns if col not in ["NAME", "COST"]]

        return {
            metric: round(row[metric] * sample_size, 2) if pd.notna(row[metric]) else None
            for metric in metric_columns
        }

    except IndexError:
        return {"Error": f"Ingredient '{ingredient}' not found in data."}

# --- Streamlit App Layout ---
st.set_page_config(page_title="Suryacore Nutrient Calculator", layout="centered")
st.title("🌾 Nutritional Metrics Calculator")
st.markdown(
    "Select an ingredient and sample size to see nutritional values calculated from per-kg data.\n\n"
    f"Currently supporting **{len(df.columns) - 2} metrics** per ingredient."
)

# --- Sidebar Inputs ---
with st.sidebar:
    st.header("⚙️ Settings")
    ingredient = st.selectbox("🌿 Choose Ingredient", sorted(df["NAME"].dropna().unique()))
    sample_size = st.slider("📦 Sample Size (kg)", min_value=1, max_value=10, value=3)

# --- Trigger Calculation ---
calculate_clicked = st.button("🧮 Calculate Nutrients")

if calculate_clicked:
    results = calculate_metrics(df, ingredient, sample_size)

    # --- Display Results ---
    if "Error" in results:
        st.error(results["Error"])
    else:
        st.success(f"✅ Nutritional values for {sample_size}kg of {ingredient}")
        # Convert results dictionary to a table
        table_data = pd.DataFrame.from_dict(results, orient='index', columns=[f"{sample_size}kg Value"])
        st.dataframe(table_data, height=600)


        # --- Filter and display chart only for first N metrics (e.g., top 20 by value)
        chart_data = pd.DataFrame({
            "Nutrient": [k for k in results if results[k] is not None],
            "Value": [v for k, v in results.items() if v is not None]
        }).sort_values(by="Value", ascending=False)

        # Optional: cap at 20 metrics to keep chart clean
        chart_data = chart_data.head(20)

        if not chart_data.empty:
            chart = alt.Chart(chart_data).mark_bar().encode(
                x=alt.X("Value:Q", title="Amount"),
                y=alt.Y("Nutrient:N", sort="-x", title="Nutrient"),
                color=alt.Color("Nutrient:N", legend=None),
                tooltip=["Nutrient", "Value"]
            ).properties(
                title=f"🔬 Top Nutrient Contributions for {sample_size}kg of {ingredient}",
                width=700,
                height=500
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.warning("⚠️ No nutrient data available to chart.")
