import streamlit as st
import pandas as pd
import re

st.set_page_config(page_icon="🚬", page_title="The Joiner")

st.image(
	"https://em-content.zobj.net/thumbs/240/apple/325/fondue_1fad5.png",
	width=100,
)

st.title("The Joiner")

# st.write("""
# The Melter is designed to streamline the process of reshaping data from a wide format to a long format. It's useful for handling CSV files exported from Beauhurst.

# **How it works:**
# 1. **Upload a CSV file:** Use the uploader widget to add your Beauhurst exported file.
# 2. **Select ID Column Names:** Choose columns that uniquely identify each row (e.g., URLs, company names).
# 3. **Select Variable Columns:** Choose the columns that you wish to transform from wide to long format (e.g., turnover, headcount).
# 4. **Transform and Download:** Click the button to transform the data and then download the reshaped CSV file.

# Ensure your CSV file is correctly formatted for optimal performance. The Variable Columns should have unique sequential numbering, eg: 1,2,3 etc. If you encounter any issues, error messages will guide you through potential fixes.
# """)


# Uses Streamlit's uploader widget to allow the user to upload a csv
uploaded_file = st.file_uploader("Upload a the main file - where you want to keep all columns (CSV)",type='csv')

right_file = st.file_uploader("Upload sedondary files - where you want to keep selected columns (CSV)", type='csv')


def column_rename(original_names):
	'''
	Renames the column names so there are no spaces and puts the sequential number in the export at the end
	'''
	new_names = original_names.copy()
	for i in range(len(new_names)):
		new_names[i] = new_names[i].replace(" (2007) ", "_")
		new_names[i] = new_names[i].replace("Head Office Address - Postcode (if UK)", "Head Office Address - Postcode (if UK)1")
		if bool(re.search(r'\d', new_names[i])) == True:
			digit_position = re.search(r"\d+", new_names[i]) # match one or more digits
			digit_str = new_names[i][digit_position.start():digit_position.end()].strip() # get full matched digit string
			new_names[i] = new_names[i].replace(digit_str, "")
			new_names[i] = new_names[i]+str(digit_str)
			new_names[i] = new_names[i].replace(" - ", "_")
			new_names[i] = new_names[i].replace(" ", "_")
			new_names[i] = new_names[i].replace("__", "_")
		else:
			new_names[i] = new_names[i].replace(" - ", "_")
			new_names[i] = new_names[i].replace(" ", "_")
	return new_names



def variable_rename(new_names):
	'''
	Creates versions of the columns names that would be suitable as stubs for the Pandas wide to long
	'''
	var_names = new_names.copy()
	for i in range(len(var_names)):
		var_names[i] = re.sub(r'[0-9]+', '', var_names[i])
	return set(var_names)


# If there is a csv, Streamlit shows it in an expandable dataframe
if uploaded_file and right_file is not None:
	file_container = st.expander("Check your uploaded CSV")
	shows = pd.read_csv(uploaded_file)
	shows_right = pd.read_csv(right_file)
	uploaded_file.seek(0)
	file_container.write(shows)
	file_container.write(shows_right)

	# Creates a dataframe from the uploaded file and creates a list of column names
	df = pd.read_csv(uploaded_file)
	df_right = pd.read_csv(right_file)

	# Check for completely blank columns
	blank_columns = df.columns[df.isna().all()].tolist()
	if blank_columns:
		st.warning(f"The following columns are completely blank and should be removed: {', '.join(blank_columns)}")

	# Check for completely blank rows
	blank_rows = df.index[df.isna().all(axis=1)].tolist()
	if blank_rows:
		st.warning(f"The following rows are completely blank and should be removed: {', '.join(map(str, blank_rows))}")

	original_names = list(df.columns.values)

	original_names_right = list(df_right.columns.values)

	# Creating a list of column names for the user to choose from
	static_options = column_rename(original_names)
	right_options = column_rename(original_names_right)

	# Creating lists of column names using Streamlit's multiselect input widget, remove id columns once selected
	static_column_names = st.multiselect("Please select the ID column name from the base spreadsheet. This is the unique identifier that you will use to match with the secondary spreadsheet. Some likely choices are Beauhurst URL, company name, and Companies House ID.",static_options)
	secondary_column_names = st.multiselect("Please select the ID column name from the secondary spreadsheet. This is the unique identifier that you will use to match with the secondary spreadsheet. Some likely choices are Beauhurst URL, company name, and Companies House ID.",right_options)
	variable_options = variable_rename([x for x in static_options if x not in static_column_names])
	variable_column_names = st.multiselect("Please select the columns that you would like to include in the merged spreadsheet. Some likely choices are turnover, headcount, investor info, SIC code, and postcode.",variable_options)

	# Renaming the dataframe columns with the altered names so that it works in the wide_to_long
	column_dictionary = dict(zip(original_names, static_options))
	df = df.rename(columns=column_dictionary)

	# When the user clicks the button, attempt the wide_to_long using the user inputs
	if st.button('Make the data long'):
		try:
			df_new = pd.wide_to_long(df, stubnames=variable_column_names, i=static_column_names, j="Number")
			@st.cache_data
			def convert_df(df):
			# Cache the conversion to prevent computation on rerun
				return df.to_csv().encode('utf-8')

			#df_new = df_new.dropna()
			csv = convert_df(df_new)

			st.download_button(
				label="Download data as CSV",
				data=csv,
				file_name='new_df.csv',
				mime='text/csv',
			)
		except ValueError as e:
			error_message = str(e)
			if "Length of passed values is x, index implies y" in error_message:
				st.error("Data Transformation Error: The number of selected columns does not match the expected format. Please review your column selections.")
			elif "cannot reindex from a duplicate axis" in error_message:
				st.error("Duplicate Column Error: There are duplicate columns in your selection. Please ensure each column is unique.")
			else:
				st.error(f"Unexpected Error: {error_message}. Please review your selections and try again. If the issue persists, contact Dan for assistance.")

	else:
		st.write('')

else:
	st.info(
		f"""
			👆 Just add a CSV, no need to alter the column names.
			"""
		)

	st.stop()
