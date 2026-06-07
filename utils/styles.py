import streamlit as st

def apply_global_styles():

    st.markdown("""
    <style>
                
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        padding-left: 1.2rem;
        padding-right: 1.2rem;
}

div[date-testid="stMetric"] {
        background-color: #f7f7f7:
        padding: 1rem;
        border-radius: 16px;                
}
                
div[data-baseweb="tab-list"] {
    gap: 8px;
}
                
div[data-baseweb="tab"] {
    border-radius: 12px;
    padding: 10px 18px;
    font-weight: 600;
}
                
div.stButton > button {
    border-radius: 12px;
}
                
div[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}
                
</style>
""", unsafe_allow_html=True)