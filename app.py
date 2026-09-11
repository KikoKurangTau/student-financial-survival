import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

st.set_page_config(page_title="Finly", page_icon="💸", layout="wide")
st.markdown("""<style>.stApp{background:radial-gradient(circle at 12% 8%,#243c7d,transparent 30%),radial-gradient(circle at 88% 12%,#146458,transparent 28%),#0b1020}.block-container{max-width:1150px;padding-top:2rem}.hero{padding:2rem;border-radius:24px;background:linear-gradient(120deg,rgba(64,90,190,.38),rgba(17,180,145,.22));margin-bottom:1.2rem}.hero h1{margin:0;color:white;font-size:2.5rem}.hero p{color:#d4ddf7}.stMetric{background:#16203a}</style>""",unsafe_allow_html=True)
st.session_state.setdefault("records",[])
st.markdown("<div class='hero'><h1>💸 Finly</h1><p>Track every rupiah you earn and spend.</p></div>",unsafe_allow_html=True)
with st.form("entry",clear_on_submit=True):
 c1,c2,c3=st.columns(3)
 with c1: kind=st.selectbox("Type",["Expense","Income"]); day=st.date_input("Date",date.today())
 with c2: category=st.selectbox("Category",["Food","Transport","Education","Living","Entertainment","Emergency","Other"]); note=st.text_input("Description")
 with c3: amount=st.number_input("Amount (Rp)",min_value=0.0,step=10000.0); need=st.selectbox("Need / Want",["Need","Want"])
 if st.form_submit_button("Save transaction") and amount>0:
  st.session_state.records.append({"Date":str(day),"Type":kind,"Category":category,"Description":note or category,"Amount":amount,"Need / Want":"Need" if kind=="Income" else need});st.rerun()
df=pd.DataFrame(st.session_state.records)
income=df.loc[df.Type=="Income","Amount"].sum() if not df.empty else 0
expense=df.loc[df.Type=="Expense","Amount"].sum() if not df.empty else 0
m1,m2,m3=st.columns(3);m1.metric("Balance",f"Rp{income-expense:,.0f}");m2.metric("Income",f"Rp{income:,.0f}");m3.metric("Expenses",f"Rp{expense:,.0f}")
if not df.empty:
 st.plotly_chart(px.bar(df[df.Type=="Expense"].groupby("Category",as_index=False).Amount.sum(),x="Category",y="Amount",color="Category",template="plotly_dark",title="Expenses by category"),use_container_width=True)
 st.dataframe(df.sort_values("Date",ascending=False),hide_index=True,use_container_width=True)
 st.download_button("Export CSV",df.to_csv(index=False).encode(),"finly-transactions.csv","text/csv")
else: st.info("Add your first income or expense above.")
