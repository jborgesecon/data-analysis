import pandas as pd
from navigation import get_file, kaggle_download


# testing navigation

# main = pd.read_csv(get_file('kaggle','economics', 'gini-coefficient.csv'))
main = pd.read_csv(get_file('kaggle','economics', 'inflation.csv'))
print(main.head())
print(main.info())
print('ok\n')

kaggle_download(dataset_name="alhamomarhotaki/global-food-prices-database-wfp", db='kaggle', schema='economics')

# main = pd.read_csv(nav.get_file('kaggle','economics', 'inflation.csv'))
# main.to_sql('inflation', nav.conn, schema='main', if_exists='replace', index=False)

# df = pd.read_sql(nav.read_sql_file('person', True), nav.conn)
# second = df['num_proposta'].unique()
# print(len(second))

# a = pd.DataFrame(nav.run_query('inflation_1'))
# print(a)
