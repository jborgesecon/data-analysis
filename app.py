import pandas as pd
import navigation as nav


test1 = pd.read_sql(nav.read_sql_file('person'), nav.postgres_conn)
cols = test1.columns.tolist()
for column in cols:
    print(column)