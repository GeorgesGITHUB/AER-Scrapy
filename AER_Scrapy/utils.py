import pandas as pd

# Wraps the native print function with a border
def cprint(*args):
    print('*')
    # print('**')
    # print('***')
    string = ''
    for arg in args: string += str(arg) + ' '
    print(string)
    # print('***')
    # print('**')
    print('*')

# From CSV, returns column values into a list
# def col_to_list('LandUnit', 'test.csv'):
def col_to_list(col, file_path):
    # Read the CSV file into a Pandas DataFrame
    df = pd.read_csv(file_path)

    # Get unique values from the "LandUnit" column
    return list( df[col].unique() )

# From CSV, returns a dictionary of a column's associate to another
# def cols_to_dict('PolyID', 'LandUnit','test.csv'):
def cols_to_dict(key_col, value_col,file_path):
    # Read the CSV file into a Pandas DataFrame
    df = pd.read_csv(file_path)

    # Group by 'PolyID' and aggregate 'LandUnit' into lists
    grouped_data = df.groupby(key_col)[value_col].apply(list).reset_index()

    # Convert grouped data into a dictionary
    return dict(zip(grouped_data[key_col], grouped_data[value_col]))