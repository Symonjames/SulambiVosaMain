import pandas as pd

df = pd.read_excel('data/member-app.xlsx')
print('Total columns:', len(df.columns))
print('\nColumn list:')
for i, col in enumerate(df.columns, 1):
    print(f'{i}. {col}')

print(f'\nTotal rows: {len(df)}')
print(f'\nFirst row sample:')
print(df.iloc[0])

















