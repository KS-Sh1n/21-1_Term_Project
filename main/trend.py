from pytrends.request import TrendReq
import pandas as pd

pytrends = TrendReq(hl="en-US", tz = 540)

def get_trending_searches(country):
    trending_df = pytrends.trending_searches(pn=country)
    trending_lst = []

    for i in range(20):
        j = trending_df.loc[i][0]
        trending_lst.append(j)

    return trending_lst

kw_list = get_trending_searches("south_korea")
pytrends.build_payload(kw_list=["로스트아크"], timeframe='today 5-y', geo="KR", gprop="")

df_rt = pytrends.related_topics()
print(df_rt)