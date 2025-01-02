import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# App Title
st.title('📊 File Uploader and Data Explorer')

# Sidebar Description
st.sidebar.title('📂 Options')
st.sidebar.info('Upload your file and explore the data interactively.')

# File Upload Section
st.header('1. Upload Your File')
uploaded_file = st.file_uploader('Upload a file (CSV, XLSX, JSON)', type=['csv', 'xlsx', 'json'])

if uploaded_file is not None:
    # Read Data
    if uploaded_file.name.endswith('.csv'):
        data = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith('.xlsx'):
        data = pd.read_excel(uploaded_file)
    elif uploaded_file.name.endswith('.json'):
        data = pd.read_json(uploaded_file)

    # Dataset Overview
    st.header('2. Dataset Overview')
    st.subheader('Preview')
    st.write(data.head())

    st.subheader('Dataset Shape')
    st.write(f'Rows: {data.shape[0]}, Columns: {data.shape[1]}')

    # Missing Values
    if data.isnull().sum().sum() > 0:
        st.warning('⚠️ Your dataset contains missing values.')
        if st.button('Drop Missing Values'):
            data = data.dropna()
            st.success('Missing values have been removed.')

    # Column Selection for Viewing
    st.header('3. Data Filtering')
    st.sidebar.subheader('Filter Options')
    columns = data.columns.tolist()
    selected_columns = st.multiselect('Select columns to view:', columns, default=columns[:2])

    if selected_columns:
        filtered_data = data[selected_columns]

        # Filtering by Column
        for col in selected_columns:
            if data[col].dtype in ['object', 'category']:
                unique_vals = data[col].unique()
                selected_vals = st.sidebar.multiselect(f'Filter {col}', unique_vals, default=unique_vals)
                filtered_data = filtered_data[filtered_data[col].isin(selected_vals)]
            else:
                min_val, max_val = float(data[col].min()), float(data[col].max())
                range_vals = st.sidebar.slider(f'Filter {col}', min_val, max_val, (min_val, max_val))
                filtered_data = filtered_data[(data[col] >= range_vals[0]) & (data[col] <= range_vals[1])]

        st.subheader('Filtered Data')
        st.dataframe(filtered_data)

    # Column Selection for Analysis
    st.header('4. Data Analysis & Visualization')
    selected_analysis_columns = st.multiselect('Select columns for analysis:', columns)

    if selected_analysis_columns:
        try:
            if len(selected_analysis_columns) == 1:
                col = selected_analysis_columns[0]

                # Statistics
                st.write(f'**{col} Statistics**')
                st.write(f'Mean: {data[col].mean():.2f}')
                st.write(f'Median: {data[col].median():.2f}')
                st.write(f'Standard Deviation: {data[col].std():.2f}')

                # Visualization
                st.subheader('Visualization')
                fig, ax = plt.subplots()
                sns.histplot(data[col], kde=True, ax=ax)
                st.pyplot(fig)
            else:
                st.write('**Correlation Matrix**')
                corr_matrix = data[selected_analysis_columns].corr()
                st.write(corr_matrix)

                fig, ax = plt.subplots(figsize=(10, 6))
                sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', ax=ax)
                st.pyplot(fig)
        except Exception as e:
            st.error(f"An error occurred: {e}")

    # Data Download
    st.header('5. Download Filtered Data')
    @st.cache
    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')

    csv = convert_df(filtered_data if 'filtered_data' in locals() else data)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name='filtered_data.csv',
        mime='text/csv',
    )
else:
    st.info('Please upload a file to start exploring.')
