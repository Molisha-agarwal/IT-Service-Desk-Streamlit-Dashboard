import os
import streamlit as st
from openai import OpenAI
import pandas as pd

def run_ai_assistant(df):

    st.sidebar.markdown("---")
    st.sidebar.subheader("🤖 AI Assistant")

    user_query = st.sidebar.text_input("Ask about your data:")

    if user_query:

        # 🔐 API Key (works everywhere)
        api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

        if not api_key:
            st.sidebar.error("API key not found")
            return

        client = OpenAI(api_key=api_key)

        # --------------------------------------------------
        # 🔹 SAFE COPY (does NOT affect your main dashboard)
        # --------------------------------------------------
        df_copy = df.copy()

        # Normalize column names
        df_copy.columns = df_copy.columns.str.strip().str.lower()

        # Rename only if needed (safe mapping)
        rename_map = {
            "request status": "status",
            "priority type": "priority",
            "created time": "created_date",
            "completed time": "closed_date",
            "technician name": "technician"
        }

        df_copy = df_copy.rename(columns=rename_map)

        # --------------------------------------------------
        # 🔹 CHECK REQUIRED COLUMNS
        # --------------------------------------------------
        required_cols = ["status", "created_date", "closed_date"]

        for col in required_cols:
            if col not in df_copy.columns:
                st.sidebar.error(f"Missing column: {col}")
                return

        # --------------------------------------------------
        # 🔹 DATE & KPI CALCULATIONS
        # --------------------------------------------------
        df_copy["created_date"] = pd.to_datetime(df_copy["created_date"], errors="coerce")
        df_copy["closed_date"] = pd.to_datetime(df_copy["closed_date"], errors="coerce")

        df_copy["closure_days"] = (
            (df_copy["closed_date"] - df_copy["created_date"])
            .dt.total_seconds() / 86400
        )

        df_copy["closure_days"] = df_copy["closure_days"].fillna(0).clip(lower=0)

        total = len(df_copy)
        closed = df_copy["status"].astype(str).str.lower().eq("closed").sum()
        pending = total - closed
        avg_close = round(df_copy["closure_days"].mean(), 2)
        sla = round((df_copy["closure_days"] <= 2).mean() * 100, 2)

        # --------------------------------------------------
        # 🔹 SUMMARY FOR AI
        # --------------------------------------------------
        sample_data = df_copy.sample(min(20, len(df_copy))).to_string()

        summary = f"""
        Dataset Information:
        Total Records: {total}

        Columns:
        {list(df_copy.columns)}

        Key Metrics:
        Total Tickets: {total}
        Closed Tickets: {closed}
        Pending Tickets: {pending}
        Average Closure Days: {avg_close}
        SLA Compliance (%): {sla}

        Sample Data:
        {sample_data}
        """

        prompt = f"""
        You are an expert IT Service Desk Data Analyst.

        Rules:
        - Answer ONLY using the dataset provided
        - Do NOT guess
        - Use numbers and insights

        {summary}

        Question:
        {user_query}
        """

        # --------------------------------------------------
        # 🔹 OPENAI CALL
        # --------------------------------------------------
        with st.sidebar.spinner("Analyzing..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )

                answer = response.choices[0].message.content
                st.sidebar.success(answer)

            except Exception as e:
                st.sidebar.error(f"Error: {str(e)}")
