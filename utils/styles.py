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
    
def apply_mobile_styles():
    import streamlit as st

    st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem;
        padding-left: 0.8rem;
        padding-right: 0.8rem;
    }

    h1 {
        font-size: 1.8rem !important;
        margin-bottom: 0.2rem !important;
    }

    h2, h3 {
        margin-top: 0.8rem !important;
        margin-bottom: 0.4rem !important;
    }

    div[data-testid="stMetric"] {
        padding: 0.6rem;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 0.8rem;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.4rem;
    }
    </style>
    """, unsafe_allow_html=True)