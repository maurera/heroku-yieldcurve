import pandas as pd
import numpy as np

# 1) Load yield curve data
# one file per year (csv)
def loaddata(type):
    #type = "3M" # OIS vs 3M
    if type=='CMT':
        df = loaddata_cmt()
    else:
        # source = '/USD '+type+'/Derived Data/'
        # stub = 'YieldCurve_USD_'+type+'_DerivedData_'
        # df = pd.concat(
        #     [pd.read_csv(source + stub + str(x) + '.csv', parse_dates=True)[['Reference Date', 'Date', 'Zero Rate']] for x in range(2007, 2019)],
        #     axis=0, sort=False, ignore_index=True)
        df = pd.read_pickle('data/USD_'+type+'.pkl')
        df.rename(columns={"Reference Date": "Date", "Date": "Maturity"},inplace=True)
        df['Date'] = pd.to_datetime(df['Date'],yearfirst=True)
        df['Maturity'] = pd.to_datetime(df['Maturity'],yearfirst=True)
        df['Term'] = (round((df['Maturity']-df['Date']).astype('timedelta64[D]')/30)).astype(int)
        df.drop_duplicates(subset=['Date','Term'],keep='last',inplace=True)

    # 2) Load shock data (single xlsx file)
    # data comes in with rows (one per country) and columns (one per term) and values (shock amount). First tab is IR Swap shocks
    #source = '2018 Market Risk Scenarios EBA.xlsx'
    sk = pd.read_pickle('data/EBA_2018_Shocks.pkl')
    sk=sk[sk['Country']=='US']
    sk = sk.filter(regex=("^[0-9]+"))
    sk = sk.transpose()
    sk.columns = ['shock']
    sk['Term'] = sk.index
    sk['Term'] = sk.index.str.replace('^([0-9]+)[^0-9]+$',r'\1',regex=True).astype(int)
    sk.loc[sk.index.str.match('^[0-9]+Y$'), 'Term']*=12
    sk.loc[sk.index.str.match('^[0-9]+Y\+'), 'Term'] = 999
    merged = df.merge(sk,how='outer',on='Term',sort=True)
    merged['shock'].fillna(method='backfill',inplace=True)
    merged.dropna(subset=['Date'],inplace=True)
    merged['Shocked']=merged['Zero Rate']+merged['shock']/100

    return merged

# Treasury data
def loaddata_cmt():
    # df_cmt = pd.read_csv('/FRED/CMT_treasury_Daily.txt',sep='\t')
    df_cmt = pd.read_pickle('data/USD_CMT.pkl')
    df_cmt.replace('.', np.NaN,inplace=True)
    df_cmt = df_cmt[df_cmt['DATE']>='2002-01-01']
    df_cmt.dropna(how='all',thresh=4,inplace=True) # Need 4 non-missing to  keep
    df_cmt = df_cmt.melt(id_vars='DATE', var_name='term_string', value_name='Zero Rate')
    df_cmt['Zero Rate'] = df_cmt['Zero Rate'].astype('float')
    df_cmt['Term'] = df_cmt['term_string'].str.replace('^DGS([0-9]+)[^0-9]*$',r'\1',regex=True).astype(int)
    df_cmt.loc[df_cmt['term_string'].str.match('^DGS[0-9]+$'), 'Term']*=12
    df_cmt.drop(columns='term_string',inplace=True)
    df_cmt['DATE'] = pd.to_datetime(df_cmt['DATE'],yearfirst=True)
    df_cmt.sort_values(by=['Term','DATE'],inplace=True)
    df_cmt.rename(columns={'DATE':'Date'},inplace=True)
    df_cmt.dropna(inplace=True)
    return df_cmt

# test1 = loaddata('CMT')
# test = loaddata_cmt()

# 'C:/Users/andrew.maurer/OneDrive - IHS Markit/Projects/StressTesting/Data/FRED/CMT_treasury_Daily.txt'
# 3) Combine shocks with yc data
#print(head)
#print(sk)

#sys.exit('asdf')

# 4) Graph
# traces=[go.Scatter(x=merged['Term'], y=merged['Zero Rate'], name='Baseline')]
# traces.append(go.Scatter(x=merged['Term'], y=merged['Shocked'], name='EBA shock'))
# layout=go.Layout(showlegend=True,xaxis={'title': 'Term (months)'},yaxis={'title': 'Rate (%)'})
# fig = go.Figure(data=traces,layout=layout)
# fig.update_xaxes(title_text='Term (months)')
# fig.update_yaxes(title_text='Rate (%)')
# py.plot(fig)