import pandas as pd

df = pd.read_excel('data/satisfaction-ratings.xlsx')
print('✓ Excel file verified:')
print(f'Total records: {len(df)}')
print(f'Volunteer responses: {len(df[df["Respondent Type"] == "Volunteer"])}')
print(f'Beneficiary responses: {len(df[df["Respondent Type"] == "Beneficiary"])}')
print(f'\nEvent titles used: {len(df["Event Title"].unique())} unique events')
print(f'Names used: {len(df["Respondent Name"].unique())} unique names')
print(f'\nSample event titles:')
for e in list(df["Event Title"].unique())[:5]:
    print(f'  - {e}')
print(f'\nSample names:')
for n in list(df["Respondent Name"].unique())[:5]:
    print(f'  - {n}')

















