# prompt: Chat help me on how to exapand the Selic time interval to daily interest

import pandas as pd
import numpy as np

def expand_interest_rates(df_reference):
    """Expands df_reference into a daily rate table."""
    daily_rates = {}
    for _, row in df_reference.iterrows():
        date_range = pd.date_range(row['dt_init'], row['dt_end'], freq='D')
        daily_rate = (1 + row['period_interest'] / 100) ** (1 / len(date_range)) - 1  # Convert to daily rate
        daily_rates.update({date: daily_rate for date in date_range})
    return daily_rates

def calculate_compound_interest(df_input, daily_rates):
    """Calculates compound interest for each investment."""
    results = []    
    for _, row in df_input.iterrows():
        date_range = pd.date_range(row['dt_investment'], row['dt_withdraw'], freq='D')
        rates = [daily_rates.get(date, 0) for date in date_range]
        compound_factor = np.prod([(1 + r) for r in rates])
        final_value = row['principal_value'] * compound_factor
        results.append(final_value)
    df_input['final_value'] = results
    return df_input

# Sample Data
input_data = {
    'dt_investment': pd.to_datetime(['2024-01-12', '2024-02-03', '2024-01-20']),
    'dt_withdraw': pd.to_datetime(['2024-07-24', '2024-08-10', '2024-06-14']),
    'principal_value': [100, 100, 100]
}
df_input = pd.DataFrame(input_data)

reference_data = {
    'dt_init': pd.to_datetime(['2024-01-15', '2024-02-15', '2024-03-15', '2024-05-15', '2024-06-15', '2024-07-15']),
    'dt_end': pd.to_datetime(['2024-02-14', '2024-03-14', '2024-05-14', '2024-06-14', '2024-07-14', '2024-08-14']),
    'period_interest': [0.97, 0.8, 1.21, 0.92, 1.11, 1.3]
}
df_reference = pd.DataFrame(reference_data)

# Compute Interest
interest_rates = expand_interest_rates(df_reference)
df_result = calculate_compound_interest(df_input, interest_rates)
print(df_result)
