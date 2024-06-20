import pandas as pd
import streamlit as st
import re

st.title("🚬 The Joiner")
st.set_page_config(page_icon="🚬", page_title="The Joiner")

# ask user for input
left_file = st.file_uploader("Upload the main file - where you want to keep all columns (CSV)",type='csv')
right_file = st.file_uploader("Upload the secondary file - where you want to keep selected columns (CSV)",type='csv')

try:

	left_df = pd.read_csv(left_file)
	right_df = pd.read_csv(right_file)

	# reformat column names and ask user to select fields
	original_names_left = list(left_df.columns.values)
	original_names_right = list(right_df.columns.values)

	variable_options = original_names_left + original_names_right
	# there could be duplicate column names here
			
	primary_column_names_list = st.selectbox("Please select the ID column name from the base spreadsheet. This is the unique identifier that you will use to match with the secondary spreadsheet. Some likely choices are Beauhurst URL, company name, and Companies House ID.",original_names_left)
	secondary_column_names_list = st.selectbox("Please select the ID column name from the secondary spreadsheet. This is the unique identifier that you will use to match with the secondary spreadsheet. Some likely choices are Beauhurst URL, company name, and Companies House ID.",original_names_right)

except:
	
	st.write('')

# join the data into a merged spreadsheet and make it available for download
if st.button('Join my data'):
	df_new = left_df.merge(right=right_df, 
        		       left_on=primary_column_names_list, 
            		       right_on=secondary_column_names_list,
            		       how='left',
			       suffixes=('_left', '_right'))

	df_new = df_new.rename(columns=lambda x: x.replace('_left', ''))
	df_new = df_new.rename(columns=lambda x: x.replace('_right', ''))

	duplicate_cols = df_new.columns.duplicated(keep='first')
	df_new = df_new.loc[:, ~duplicate_cols]
	df_new.drop(columns=secondary_column_names_list, inplace=True)

	def convert_df(df):
		# Cache the conversion to prevent computation on rerun
		return df.to_csv(index=False).encode('utf-8')
		
	csv = convert_df(df_new)
		
	st.download_button(label="Download data as CSV",
			   data=csv,
			   file_name='new_df.csv',
			   mime='text/csv')

else:
	st.info(
		f"""
		👆 Just add a CSV, no need to alter the column names.
		"""
		)

	st.stop()
