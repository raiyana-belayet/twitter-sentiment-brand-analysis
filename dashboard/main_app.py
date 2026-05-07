import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="SentimentMetric | Sentiment AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a modern "SaaS" look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #ececf1;
    }
    div[data-testid="stExpander"] { border: none; box-shadow: none; }
    </style>
    """, unsafe_allow_html=True)

# 2. DATA LOADING ENGINE
@st.cache_data
def load_and_clean_data():
    cols = ['ID', 'Entity', 'Sentiment', 'Content']
    try:
        df = pd.read_csv('twitter_training.csv', names=cols, header=None)
        df.dropna(subset=['Content'], inplace=True)
        # Clean text for better NLP visuals
        df['Content'] = df['Content'].astype(str).str.replace(r'http\S+|@\S+', '', regex=True)
        return df
    except FileNotFoundError:
        st.error("❌ 'twitter_training.csv' not found. Please place it in the project folder.")
        return pd.DataFrame()

df = load_and_clean_data()

# --- 3. DYNAMIC SIDEBAR NAVIGATION ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=80)
st.sidebar.title("SentimentMetric")
st.sidebar.markdown("---")

# The "Page Switcher"
page = st.sidebar.radio("Navigate To:", ["🎯 Deep Dive", "⚔️ Competitor Battle", "🤖 Prediction Lab"])
st.sidebar.divider()

if not df.empty:
    all_entities = sorted(df['Entity'].unique())

    # ==========================================
    # PAGE 1: DEEP DIVE
    # ==========================================
    if page == "🎯 Deep Dive":
        # Dynamic Sidebar for this page
        st.sidebar.subheader("Deep Dive Filters")
        selected_entity = st.sidebar.selectbox("Select Target Brand", all_entities)
        sample_size = st.sidebar.slider("Analysis Granularity", 100, 2000, 500)
        st.sidebar.info("Analyze a single brand's reputation in detail.")

        # Main Content
        st.title(f"Reputation Analysis: {selected_entity}")
        filtered_df = df[df['Entity'] == selected_entity]
        total_vol = len(filtered_df)
        
        # Metrics
        sent_counts = filtered_df['Sentiment'].value_counts(normalize=True) * 100
        pos_rate = sent_counts.get('Positive', 0)
        neg_rate = sent_counts.get('Negative', 0)
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Volume", f"{total_vol:,}")
        m2.metric("Positive Sentiment", f"{pos_rate:.1f}%")
        m3.metric("Toxicity Rate", f"{neg_rate:.1f}%", delta="High Risk" if neg_rate > 35 else "Stable", delta_color="inverse")
        m4.metric("Engagement", "Active")

        st.divider()

        # Charts
        col_l, col_r = st.columns([2, 1])
        with col_l:
            st.subheader("Sentiment Volume Trend")
            fig_bar = px.histogram(filtered_df, x="Sentiment", color="Sentiment",
                                   color_discrete_map={'Positive': '#2ecc71', 'Negative': '#e74c3c', 'Neutral': '#3498db', 'Irrelevant': '#95a5a6'},
                                   template="plotly_white", height=400)
            st.plotly_chart(fig_bar, use_container_width=True)
        with col_r:
            st.subheader("Share of Voice")
            fig_pie = px.pie(filtered_df, names='Sentiment', hole=0.5, color='Sentiment',
                             color_discrete_map={'Positive': '#2ecc71', 'Negative': '#e74c3c', 'Neutral': '#3498db', 'Irrelevant': '#95a5a6'})
            st.plotly_chart(fig_pie, use_container_width=True)

        # Word Clouds
        st.divider()
        st.subheader("Key Sentiment Drivers")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("✅ **Positive Drivers**")
            pos_content = filtered_df[filtered_df['Sentiment'] == 'Positive']['Content']
            if not pos_content.empty:
                pos_text = " ".join(pos_content.sample(min(len(pos_content), sample_size)))
                st.image(WordCloud(width=800, height=500, background_color='white', colormap='Greens').generate(pos_text).to_array(), use_container_width=True)
        with c2:
            st.markdown("🚨 **Negative Drivers**")
            neg_content = filtered_df[filtered_df['Sentiment'] == 'Negative']['Content']
            if not neg_content.empty:
                neg_text = " ".join(neg_content.sample(min(len(neg_content), sample_size)))
                st.image(WordCloud(width=800, height=500, background_color='white', colormap='Reds').generate(neg_text).to_array(), use_container_width=True)

    # ==========================================
    # PAGE 2: COMPETITOR BATTLE
    # ==========================================
    elif page == "⚔️ Competitor Battle":
        # Dynamic Sidebar for this page
        st.sidebar.subheader("Battle Controls")
        st.sidebar.write("Compare the sentiment footprint of two rival entities.")
        st.sidebar.warning("Ensure you select two different brands for a valid comparison.")
        
        st.title("⚔️ Competitor Battle Mode")
        
        # Selectors in main area for easy comparison
        b_col1, b_col2 = st.columns(2)
        with b_col1:
            brand_a = st.selectbox("Select Brand A", all_entities, index=0)
        with b_col2:
            brand_b = st.selectbox("Select Brand B", all_entities, index=1)
        
        battle_df = df[df['Entity'].isin([brand_a, brand_b])]
        
        # Comparison Chart
        st.subheader("Side-by-Side Sentiment Distribution")
        fig_battle = px.histogram(battle_df, x="Sentiment", color="Entity", barmode="group",
                                  template="plotly_white", color_discrete_sequence=px.colors.qualitative.Bold,
                                  category_orders={"Sentiment": ["Positive", "Negative", "Neutral", "Irrelevant"]})
        st.plotly_chart(fig_battle, use_container_width=True)
        
        # Leaderboard
        st.divider()
        st.subheader("🚩 Toxicity Benchmarking (All Brands)")
        all_stats = df.groupby('Entity')['Sentiment'].value_counts(normalize=True).unstack().fillna(0)
        all_stats = (all_stats['Negative'] * 100).sort_values(ascending=False).reset_index()
        all_stats.columns = ['Entity', 'Negative Sentiment %']
        
        def highlight_comp(s):
            return ['background-color: #ff4b4b; color: white' if v in [brand_a, brand_b] else '' for v in s]
        
        st.dataframe(all_stats.style.apply(highlight_comp, subset=['Entity']).format({'Negative Sentiment %': '{:.1f}%'}), use_container_width=True)

    # ==========================================
    # PAGE 3: PREDICTION LAB
    # ==========================================
    elif page == "🤖 Prediction Lab":
        # Dynamic Sidebar for this page
        st.sidebar.subheader("ML Model Status")
        st.sidebar.success("Model: Operational")
        st.sidebar.write("Method: Keyword Vectorization")
        st.sidebar.info("This tool simulates how a classifier evaluates new social media content.")

        st.title("🤖 AI Sentiment Prediction Lab")
        st.markdown("Test the logic of our sentiment engine by entering custom text below.")
        
        user_input = st.text_area("Input Mock Tweet / Feedback:", placeholder="Example: I love the gameplay but the servers are laggy...", height=150)
        
        if st.button("Predict Sentiment"):
            if user_input:
                pos_words = ['love', 'great', 'best', 'awesome', 'good', 'happy', 'amazing', 'fun', 'enjoy']
                neg_words = ['hate', 'bad', 'trash', 'broken', 'worst', 'fix', 'lag', 'terrible', 'boring']
                
                score = sum(1 for w in user_input.lower().split() if w in pos_words) - \
                        sum(1 for w in user_input.lower().split() if w in neg_words)
                
                st.divider()
                if score > 0:
                    st.success(f"### Predicted Sentiment: **POSITIVE** ✨")
                    st.balloons()
                elif score < 0:
                    st.error(f"### Predicted Sentiment: **NEGATIVE** 🚨")
                else:
                    st.info(f"### Predicted Sentiment: **NEUTRAL** 😐")
                
                st.write(f"Confidence Metric:")
                st.progress(max(0, min(1.0, 0.5 + (score * 0.1))))
            else:
                st.warning("Please enter text to analyze.")

else:
    st.warning("Please check your data source to begin analysis.")
