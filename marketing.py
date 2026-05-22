import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(layout="wide", page_title="마케팅 투자 대시보드")

# 데이터 로드 및 전처리
@st.cache_data
def load_data():
    marketing = pd.read_csv('marketing_campaign_dataset.csv')
    # 원본 Acquisition_Cost 문자열을 별도 컬럼으로 보존
    marketing['Acquisition_Cost_raw'] = marketing['Acquisition_Cost']
    # Acquisition_Cost를 숫자로 변환 ($와 콤마 제거)
    marketing['Acquisition_Cost'] = marketing['Acquisition_Cost'].str.replace('$', '', regex=False).str.replace(',', '', regex=False).astype(float)
    marketing['Date'] = pd.to_datetime(marketing['Date'])
    return marketing

marketing = load_data()

# 사이드바 필터
st.sidebar.title('🔎 필터')
start_date, end_date = st.sidebar.date_input(
    '기간',
    [marketing['Date'].min().date(), marketing['Date'].max().date()]
)
selected_channels = st.sidebar.multiselect(
    '채널',
    options=sorted(marketing['Channel_Used'].unique()),
    default=sorted(marketing['Channel_Used'].unique())
)
selected_locations = st.sidebar.multiselect(
    '지역',
    options=sorted(marketing['Location'].unique()),
    default=sorted(marketing['Location'].unique())
)
selected_types = st.sidebar.multiselect(
    '캠페인 타입',
    options=sorted(marketing['Campaign_Type'].unique()),
    default=sorted(marketing['Campaign_Type'].unique())
)
roi_min = st.sidebar.slider(
    'ROI 최소값',
    float(marketing['ROI'].min()),
    float(marketing['ROI'].max()),
    float(marketing['ROI'].min()),
    step=0.01
)
cost_max = st.sidebar.slider(
    'Acquisition Cost 최대값',
    float(marketing['Acquisition_Cost'].min()),
    float(marketing['Acquisition_Cost'].max()),
    float(marketing['Acquisition_Cost'].max()),
    step=100.0
)
conversion_min = st.sidebar.slider(
    '전환율 최소값',
    float(marketing['Conversion_Rate'].min()),
    float(marketing['Conversion_Rate'].max()),
    float(marketing['Conversion_Rate'].min()),
    step=0.001
)

filtered = marketing[
    (marketing['Date'] >= pd.to_datetime(start_date)) &
    (marketing['Date'] <= pd.to_datetime(end_date)) &
    (marketing['Channel_Used'].isin(selected_channels)) &
    (marketing['Location'].isin(selected_locations)) &
    (marketing['Campaign_Type'].isin(selected_types)) &
    (marketing['ROI'] >= roi_min) &
    (marketing['Acquisition_Cost'] <= cost_max) &
    (marketing['Conversion_Rate'] >= conversion_min)
]

if filtered.empty:
    st.title('📊 마케팅 투자 대시보드')
    st.warning('선택된 조건에 맞는 데이터가 없습니다. 필터를 조정하세요.')
    st.stop()

st.title('📊 마케팅 투자 대시보드')
st.markdown("---")

# ============ 1. 핵심 KPI ============
st.subheader('🎯 핵심 KPI')
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    avg_roi = filtered['ROI'].mean()
    st.metric("평균 ROI", f"{avg_roi:.2%}")

with col2:
    avg_conversion = filtered['Conversion_Rate'].mean()
    st.metric("평균 전환율", f"{avg_conversion:.2%}")

with col3:
    avg_cost = filtered['Acquisition_Cost'].mean()
    st.metric("평균 고객획득비용", f"${avg_cost:,.0f}")

with col4:
    total_clicks = filtered['Clicks'].sum()
    st.metric("총 클릭", f"{total_clicks:,.0f}")

with col5:
    avg_engagement = filtered['Engagement_Score'].mean()
    st.metric("평균 참여도", f"{avg_engagement:.2f}/10")

st.markdown("---")

# ============ 2. 채널별 성과 ============
st.subheader('📡 채널별 성과 분석')
channel_analysis = filtered.groupby('Channel_Used').agg({
    'ROI': 'mean',
    'Conversion_Rate': 'mean',
    'Acquisition_Cost': 'mean',
    'Clicks': 'sum',
    'Impressions': 'sum'
}).round(4).sort_values('ROI', ascending=False)

col1, col2 = st.columns(2)

with col1:
    fig_roi = px.bar(channel_analysis.reset_index(), x='Channel_Used', y='ROI', 
                     title='채널별 평균 ROI', color='ROI', color_continuous_scale='greens')
    st.plotly_chart(fig_roi, use_container_width=True)

st.dataframe(channel_analysis, use_container_width=True)

st.markdown("---")

# ============ 3. 지역별 성과 ============
st.subheader('🌍 지역별 성과 분석')
location_analysis = filtered.groupby('Location').agg({
    'ROI': 'mean',
    'Conversion_Rate': 'mean',
    'Acquisition_Cost': 'mean'
}).round(2).sort_values('ROI', ascending=False)

col1, col2 = st.columns(2)

with col1:
    fig_location_roi = px.bar(location_analysis.reset_index().head(15), x='Location', y='ROI',
                             title='지역별 ROI TOP 15', color='ROI', color_continuous_scale='reds')
    fig_location_roi.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_location_roi, use_container_width=True)

st.markdown("---")

# ============ 4. 캠페인 타입별 효율성 ============
st.subheader('📢 캠페인 타입별 효율성')
campaign_type_analysis = filtered.groupby('Campaign_Type').agg({
    'ROI': 'mean',
    'Conversion_Rate': 'mean',
    'Clicks': 'sum',
    'Acquisition_Cost': 'mean'
}).round(2).sort_values('ROI', ascending=False)

fig_campaign = px.bar(campaign_type_analysis.reset_index(), x='Campaign_Type', y='ROI',
                     title='캠페인 타입별 평균 ROI (배수)', color='ROI')
st.plotly_chart(fig_campaign, use_container_width=True)

st.dataframe(campaign_type_analysis, use_container_width=True)

st.markdown("---")

# ============ 5. Cost vs 성과 관계 ============
st.subheader('💰 Cost vs ROI 분석 (비용 대비 효율)')
sample_size = min(len(filtered), 5000)
fig_scatter = px.scatter(filtered.sample(sample_size), x='Acquisition_Cost', y='ROI',
                         color='Conversion_Rate', size='Clicks',
                         title='고객획득비용 vs ROI (색상: 전환율, 크기: 클릭수)',
                         hover_data=['Company', 'Channel_Used'])
st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("💡 **인사이트**: 좌상단(저비용-고ROI) 캠페인에 투자 집중")

st.markdown("---")

# ============ 6. 고객 세그먼트별 ROI ============
st.subheader('👥 고객 세그먼트별 ROI')
segment_analysis = filtered.groupby('Customer_Segment').agg({
    'ROI': 'mean',
    'Conversion_Rate': 'mean',
    'Clicks': 'sum'
}).round(4).sort_values('ROI', ascending=False)

col1, col2 = st.columns(2)

with col1:
    fig_seg_roi = px.bar(segment_analysis.reset_index(), x='Customer_Segment', y='ROI',
                        title='세그먼트별 평균 ROI', color='ROI', color_continuous_scale='viridis')
    fig_seg_roi.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_seg_roi, use_container_width=True)

with col2:
    st.dataframe(segment_analysis, use_container_width=True)

st.markdown("---")

# ============ 7. 참여도와 ROI 상관관계 ============
st.subheader('📈 참여도(Engagement)와 ROI 상관관계')
engagement_roi = filtered.groupby('Engagement_Score').agg({
    'ROI': 'mean',
    'Conversion_Rate': 'mean',
    'Clicks': 'sum'
}).reset_index().sort_values('Engagement_Score')

fig_engagement = px.line(engagement_roi, x='Engagement_Score', y='ROI',
                         title='참여도 점수별 평균 ROI', markers=True)
st.plotly_chart(fig_engagement, use_container_width=True)

st.markdown("💡 **검증**: 참여도가 높을수록 ROI도 높은 경향 → 참여도 중요 지표")

st.markdown("---")

# ============ 8. 추천 분석 ============
st.subheader('💼 투자자 추천사항')

# 최고 성과 채널
best_channel_data = channel_analysis.reset_index().iloc[0]
best_channel_name = best_channel_data['Channel_Used']
best_channel_roi = best_channel_data['ROI']

# 최고 성과 지역
best_location = location_analysis.reset_index().iloc[0]

# 최고 전환율 세그먼트
best_segment = segment_analysis.reset_index().sort_values('Conversion_Rate', ascending=False).iloc[0]

col1, col2, col3 = st.columns(3)

with col1:
    st.success(f"""
    ✅ **최고 ROI 채널**
    
    채널: {best_channel_name}
    
    ROI: {best_channel_roi:.2%}
    """)

with col2:
    st.info(f"""
    🎯 **최고 수익 지역**
    
    지역: {best_location['Location']}
    
    ROI: {best_location['ROI']:.2%}
    """)

with col3:
    st.warning(f"""
    👥 **최고 전환율 세그먼트**
    
    세그먼트: {best_segment['Customer_Segment']}
    
    전환율: {best_segment['Conversion_Rate']:.2%}
    """)
with st.expander("🔍 원본 데이터 통계 요약 및 미리보기"):
    st.write(f"**선택된 데이터 크기**: 행 {len(filtered):,}개, 열 {len(filtered.columns)}개")
    st.write(f"**보유 칼럼**: {list(filtered.columns)}")
    
    st.subheader('📋 통계 요약')
    st.dataframe(filtered.describe(), use_container_width=True)

    st.subheader('👀 데이터 미리보기 (상위 5행)')
    st.dataframe(filtered.head(), use_container_width=True)

    st.subheader('📊 수치형 컬럼 분포 분석')
    if st.checkbox("컬럼 분포 시각화 활성화"):
        num_col = st.selectbox("분석할 칼럼을 선택하세요:", filtered.select_dtypes(include='number').columns)
        # bar_chart 대신 연속형 분포를 보여주는 histogram 사용
        fig_hist = px.histogram(filtered, x=num_col, title=f'{num_col} 분포 히스토그램')
        st.plotly_chart(fig_hist, use_container_width=True)
