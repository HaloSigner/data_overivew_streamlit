import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# App Title
st.title('File Uploader and Viewer')

# File Upload Section
uploaded_file = st.file_uploader('Upload File', type=['csv', 'xlsx', 'json'])

# Checking for Data Upload
if uploaded_file is not None:
    # Read Data
    if uploaded_file.name.endswith('.csv'):
        data = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith('.xlsx'):
        data = pd.read_excel(uploaded_file)
    elif uploaded_file.name.endswith('.json'):
        data = pd.read_json(uploaded_file)

    # Description of Data
    st.subheader('Dataset Preview')
    st.write(data.head())

    # Data shape 
    st.write(f'Shape of the dataset: {data.shape}')

    # Basic Statistics
    st.subheader('Basic Statistics')
    st.write(data.describe())

    # Missing Value Handling
    if data.isnull().sum().sum() > 0:
        st.warning('Dataset contains missing values.')
        if st.button('Drop Missing Values'):
            data = data.dropna()
            st.success('Missing values dropped.')

    # Column Selection for Viewing
    st.subheader('Select Columns for Viewing')
    columns = data.columns.tolist()
    selected_columns_view = st.multiselect('Select columns to view and filter', columns, default=columns[:2])

    if selected_columns_view:
        st.subheader('Filtered Data for Viewing')
        filtered_data = data[selected_columns_view]

        # Data Filtering
        st.sidebar.header('Filter Data')
        for col in selected_columns_view:
            if filtered_data[col].dtype == 'object' or filtered_data[col].dtype.name == 'category':
                unique_vals = filtered_data[col].unique()
                selected_val = st.sidebar.multiselect(f'Filter {col}', unique_vals, default=unique_vals)
                filtered_data = filtered_data[filtered_data[col].isin(selected_val)]
            else:
                min_val = float(filtered_data[col].min())
                max_val = float(filtered_data[col].max())
                range_val = st.sidebar.slider(f'Filter {col}', min_val, max_val, (min_val, max_val))
                filtered_data = filtered_data[(filtered_data[col] >= range_val[0]) & (filtered_data[col] <= range_val[1])]

        st.dataframe(filtered_data)
    else:
        st.write('No columns selected for viewing.')

    # Column Selection for Analysis
    st.subheader('Select Columns for Analysis')
    selected_columns_analysis = st.multiselect('Select columns for analysis', selected_columns_view, key='analysis')

    if selected_columns_analysis:
        st.subheader('Data Analysis')
        try:
            if len(selected_columns_analysis) == 1:
                column = selected_columns_analysis[0]
                st.write(f"Mean of {column}: {data[column].mean()}")
                st.write(f"Median of {column}: {data[column].median()}")
                st.write(f"Standard Deviation of {column}: {data[column].std()}")

                # Visualization for single column
                st.subheader('Visualization')
                fig, ax = plt.subplots()
                sns.histplot(data[column], kde=True, ax=ax)
                ax.set_title(f'Distribution of {column}')
                st.pyplot(fig)

                # Boxplot
                fig, ax = plt.subplots()
                sns.boxplot(data=data, x=column, ax=ax)
                ax.set_title(f'Boxplot of {column}')
                st.pyplot(fig)

            elif len(selected_columns_analysis) > 1:
                st.write("Correlation Matrix:")
                correlation_matrix = data[selected_columns_analysis].corr()
                st.write(correlation_matrix)

                # Visualization for correlation matrix
                st.subheader('Correlation Heatmap')
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', ax=ax)
                st.pyplot(fig)

                # Pair Plot
                st.subheader('Pair Plot')
                fig = sns.pairplot(data[selected_columns_analysis])
                st.pyplot(fig)

        except Exception as e:
            st.error(f"An error occurred while performing analysis: {e}")
    else:
        st.write('No columns selected for analysis.')

    # Data Download
    @st.cache
    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')

    csv = convert_df(filtered_data if 'filtered_data' in locals() else data)
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='filtered_data.csv',
        mime='text/csv',
    )
else:
    st.write('Please upload a CSV file to proceed.')
