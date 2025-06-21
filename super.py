import pandas as pd
import re
import io

# Input data
data = 'Airline Code;DelayTimes;FlightCodes;To_From\nAir Canada (!);[21, 40];20015.0;WAterLoo_NEWYork\n<Air France> (12);[];;Montreal_TORONTO\n(Porter Airways. );[60, 22, 87];20035.0;CALgary_Ottawa\n12. Air France;[78, 66];;Ottawa_VANcouvER\n""".\\.Lufthansa.\\.""";[12, 33];20055.0;london_MONTreal\n'

# Create DataFrame
df = pd.read_csv(io.StringIO(data), sep=';')

# 1. Generate FlightCodes sequence
first_valid = df['FlightCodes'].first_valid_index()
base_value = float(df.loc[first_valid, 'FlightCodes']) - first_valid*10
df['FlightCodes'] = [int(base_value + i*10) for i in range(len(df))]

# 2. Split To_From and clean city names
def format_city(city):
    # Handle special case for New York
    if 'newyork' in city.lower():
        return 'New York'
    
    # Handle multi-word cities (like San Francisco would become "San Francisco")
    return ' '.join(word.capitalize() for word in re.split(r'(\W+)', city.lower()) if word.isalpha())

# Split and clean cities
cities = df['To_From'].str.split('_', expand=True)
df['From'] = cities[0].apply(format_city)
df['To'] = cities[1].apply(format_city)
df = df.drop(columns=['To_From'])

# 3. Clean and standardize airline names
def clean_airline(name):
    # Remove punctuation
    cleaned = re.sub(r'[^\w\s]', '', name).strip()
    # Remove numbers from beginning
    return re.sub(r'^\d+\s*', '', cleaned)

def standardize_airline(name):
    # Standardize Air France naming
    if "air france" in name.lower():
        digits = ''.join(filter(str.isdigit, name))
        return f"Air France {digits}" if digits else "Air France"
    return name

df['Airline Code'] = df['Airline Code'].apply(clean_airline).apply(standardize_airline)

# Generate final output
output = df[['Airline Code', 'DelayTimes', 'FlightCodes', 'From', 'To']].to_csv(sep=';', index=False)
print(output)