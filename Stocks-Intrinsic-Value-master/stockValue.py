# Roi Solomon
# %%
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import json
import requests
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# Settings to produce nice plots in a Jupyter Notebook
plt.style.use('fivethirtyeight')
plt.rcParams['figure.figsize'] = [12, 6]


def get_jsonparsed_data(url):
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return json.loads(data)


# API URL and Key setup
base_url = "https://financialmodelingprep.com/api/v3/"
apiKey = ""
ticker = "AAPL"


# CashFlow Values For 4 Last Quarters
q_cash_flow_statement = pd.DataFrame(get_jsonparsed_data(
    base_url + 'cash-flow-statement/' + ticker + '?period=quarter' + '&apikey=' + apiKey))
q_cash_flow_statement = q_cash_flow_statement.set_index(
    'date').iloc[:4]  # Extracting data of 4 last quartes
q_cash_flow_statement.apply(pd.to_numeric, errors='coerce')

q_cash_flow_statement.iloc[:, 4:].head()

# CashFlow Values For Anuual statement
cash_flow_statement = pd.DataFrame(get_jsonparsed_data(
    base_url + 'cash-flow-statement/' + ticker + '?apikey=' + apiKey))
cash_flow_statement = cash_flow_statement.set_index('date')
cash_flow_statement = cash_flow_statement.apply(pd.to_numeric, errors='coerce')

cash_flow_statement.iloc[:, 4:].head()

# Cash Flow (Annual + TTM)
ttm_cash_flow_statement = q_cash_flow_statement.sum()  # sum last 4 quartes
cash_flow_statement = cash_flow_statement[::-1].append(
    ttm_cash_flow_statement.rename('TTM')).drop(['netIncome'], axis=1)
# reversing the list th show most recent ones first
final_cash_flow_statement = cash_flow_statement[::-1]
final_cash_flow_statement.iloc[:, 4].head()

final_cash_flow_statement[['freeCashFlow']].iloc[::-
                                                 1].iloc[-15:].plot(kind='bar', title=ticker + ' Cash Flows')
plt.show()
plt.savefig('Plots/CashFlowsChart.png')


# Quarterly Balance sheets
q_balance_sheet_statement = pd.DataFrame(get_jsonparsed_data(
    base_url + 'balance-sheet-statement/' + ticker + '?period=quarter' + '&apikey=' + apiKey))
q_balance_sheet_statement = q_balance_sheet_statement.set_index('date')
q_balance_sheet_statement = q_balance_sheet_statement.apply(
    pd.to_numeric, errors='coerce')
q_balance_sheet_statement.iloc[:, 4].head()

# Free Cash Flow, Total Debt, Cash and Short Term Investments
cash_flow = final_cash_flow_statement.iloc[0]['freeCashFlow']
total_debt = q_balance_sheet_statement.iloc[0]['totalDebt']
cash_and_ST_investments = q_balance_sheet_statement.iloc[0]['cashAndShortTermInvestments']


# List of data we want to extract from Finviz Table
metric = ['Price', 'EPS next 5Y', 'Beta', 'Shs Outstand']


def fundamental_metric(soup, metric):
    # the table which stores the data in Finviz has html table attribute class of 'snapshot-td2
    return soup.find(text=metric).find_next(class_='snapshot-td2').text


def get_finviz_data(ticker):
    try:
        url = ("http://finviz.com/quote.ashx?t=" + ticker.lower())
        soup = bs(requests.get(url, headers={
                  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}).content)
        dict_finviz = {}
        for m in metric:
            dict_finviz[m] = fundamental_metric(soup, m)
        for key, value in dict_finviz.items():
            # replace percentages
            if (value[-1] == '%'):
                dict_finviz[key] = value[:-1]
                dict_finviz[key] = float(dict_finviz[key])
            # billion
            if (value[-1] == 'B'):
                dict_finviz[key] = value[:-1]
                dict_finviz[key] = float(dict_finviz[key])*1000000000
            # milion
            if (value[-1] == 'M'):
                dict_finviz[key] = value[:-1]
                dict_finviz[key] = float(dict_finviz[key])*1000000
            try:
                dict_finviz[key] = float(dict_finviz[key])
            except:
                pass
    except Exception as e:
        print(e)
        print('Not Successful Parsin ' + ticker + 'data.')
    return dict_finviz


finviz_data = get_finviz_data(ticker)

print(finviz_data)

# Estimate Discount Rate from Beta
Beta = finviz_data['Beta']

dicount_rate = 7
if(Beta < 0.80):
    discount_rate = 5
elif(Beta >= 0.80 and Beta < 1):
    discount_rate = 6
elif(Beta >= 1 and Beta < 1.1):
    discount_rate = 6.5
elif(Beta >= 1.1 and Beta < 1.2):
    discount_rate = 7
elif(Beta >= 1.2 and Beta < 1.3):
    discount_rate = 7.5
elif(Beta >= 1.3 and Beta < 1.4):
    discount_rate = 8
elif(Beta >= 1.4 and Beta < 1.6):
    discount_rate = 8.5
elif(Beta >= 1.61):
    discount_rate = 9


EPS_growth_5Y = finviz_data['EPS next 5Y']
# half the previous growth rate, conservative estimate
EPS_growth_6Y_to_10Y = EPS_growth_5Y/2
# Slightly higher than long term inflation rate, conservative estimate
EPS_growth_11Y_to_20Y = np.minimum(EPS_growth_6Y_to_10Y, 4)

shares_outstanding = finviz_data['Shs Outstand']


print("Free Cash Flow: {}".format(cash_flow))
print("Total Debt: {}".format(total_debt))
print("Cash and ST Invesments: {}".format(cash_and_ST_investments))

print("EPS Growth 5Y: {}".format(EPS_growth_5Y))
print("EPS Growth 6Y to 10Y: {}".format(EPS_growth_6Y_to_10Y))
print("EPS Growth 11Y to 20Y: {}".format(EPS_growth_11Y_to_20Y))

print("Discount Rate: {}".format(discount_rate))

print("Shares Outstanding: {}".format(shares_outstanding))


def calculate_intrinsic_value(cash_flow, total_debt, cash_and_ST_investments,
                              EPS_growth_5Y, EPS_growth_6Y_to_10Y, EPS_growth_11Y_to_20Y,
                              shares_outstanding, discounted_rate):

    # Convert all the percentages to decimal
    EPS_growth_5Y = EPS_growth_5Y/100
    EPS_growth_6Y_to_10Y = EPS_growth_6Y_to_10Y/100
    EPS_growth_11Y_to_20Y = EPS_growth_11Y_to_20Y/100
    discounted_rate_d = discount_rate/100
    print("Discounted Cash Flows: \n")

    # Lists of projected cash flows from year 1 to year 20
    cash_flow_list = []
    cash_flow_discounted_list = []
    year_list = []

    # Years 1 to 5
    for year in range(1, 6):
        year_list.append(year)
        cash_flow *= (1 + EPS_growth_5Y)
        cash_flow_list.append(cash_flow)
        cash_flow_discounted = cash_flow/((1 + discounted_rate_d)**year)
        cash_flow_discounted_list.append(cash_flow_discounted)
        # Print out the projected discounted cash flows
        # print("Year " + str(year) + ": $" + str(cash_flow_discounted))

    # Years 6 to 10
    for year in range(6, 11):
        year_list.append(year)
        cash_flow *= (1 + EPS_growth_6Y_to_10Y)
        cash_flow_list.append(cash_flow)
        cash_flow_discounted = cash_flow/((1 + discounted_rate_d)**year)
        cash_flow_discounted_list.append(cash_flow_discounted)
        # Print out the projected discounted cash flows
        # print("Year " + str(year) + ": $" + str(cash_flow_discounted))

    # Years 11 to 20
    for year in range(11, 21):
        year_list.append(year)
        cash_flow *= (1 + EPS_growth_11Y_to_20Y)
        cash_flow_list.append(cash_flow)
        cash_flow_discounted = cash_flow/((1 + discounted_rate_d)**year)
        cash_flow_discounted_list.append(cash_flow_discounted)
        # Print out the projected discounted cash flows
        # print("Year " + str(year) + ": $" + str(cash_flow_discounted))

    intrinsic_value = (sum(cash_flow_discounted_list) -
                       total_debt + cash_and_ST_investments)/shares_outstanding
    df = pd.DataFrame.from_dict({'Year': year_list, 'Cash Flow': cash_flow_list,
                                 'Discounted Cash Flow': cash_flow_discounted_list})
    df.index = df.Year

    df2 = pd.DataFrame.from_dict(
        {'Year': year_list, 'Discounted Cash Flow': map(lambda c: "$" + str(c), cash_flow_discounted_list)})
    df2 = df2.set_index('Year')
    print(df2)

    df.plot(kind='bar', title="Projected Cash Flows of " + ticker)
    plt.show()
    plt.savefig('Plots/ProjectedCashFlows.png')

    return intrinsic_value


intrinsic_value = calculate_intrinsic_value(cash_flow, total_debt, cash_and_ST_investments,
                                            EPS_growth_5Y, EPS_growth_6Y_to_10Y, EPS_growth_11Y_to_20Y,
                                            shares_outstanding, discount_rate)


print("The Intrinsic Value of {} is: {}".format(ticker, intrinsic_value))
current_price = finviz_data['Price']
print("Current Price is: {}".format(current_price))
print("Margin of Safety:", (1-current_price/intrinsic_value)*100)

# %%

# %%

# %%
