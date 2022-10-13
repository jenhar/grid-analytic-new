
import pandas as pd
import geopandas as gpd
import numpy as np
from sklearn.preprocessing import MinMaxScaler


def getValueCount(df2,travel_npx, supply_value):
    sp=df2[['gid',supply_value]][df2[supply_value]>0].set_index('gid')[supply_value].to_dict()
    for i in travel_npx.columns:
        travel_npx[i]=sp.get(i)

    return travel_npx.to_numpy()




class analystTeams:
    
 

    def gridAnalyst(bogor_pop, df2,chi_cost, eco_demo, df):

        bogor_pop=bogor_pop[['gid','geometry']]
        supply=df2.set_index('gid')
        demand=bogor_pop.set_index('gid')
        demand_locations = list(set(chi_cost['origin']) & set(demand.index))

        demand_df=demand.loc[demand_locations]
        demand_df1=demand_df.copy()
        demand_df1['samp']=0
        demand_df1=demand_df1.drop(columns='geometry')

        eco_demo=eco_demo.set_index('gid')

        sc=[]

        for i in df.iterrows():
            types=i[1]['type']
            options=i[1]['Options']
            supply_value=i[1]['Parameter']
            influence=i[1]['Influence']

            mins=i[1]['Min_Threshold']
            maxx=i[1]['Max_Threshold']
            score=i[1]['Score']

            sc.append(supply_value+'_score')


            if types =='POI':

                supply_df=supply[supply[supply_value]>0]
                supply_dest=supply_df.index.values.tolist()
                supply_locations = list(set(chi_cost['dest'])   & set(supply_df.index))


             
                cost=chi_cost[chi_cost.dest.isin(supply_dest)]
                cost_pivot =cost.pivot('origin','dest', values='cost')


                travel_np  = cost_pivot.loc[demand_locations, supply_locations].to_numpy()
                travel_npx  = cost_pivot.loc[demand_locations, supply_locations]
                supply_count=getValueCount(df2,travel_npx, supply_value)

                if influence=='Positive':

                    mask=(travel_np >=mins) & (travel_np <=maxx)

                    travel_mask=np.where(mask, travel_np, np.NaN)
                    supply_mask=np.where(mask, supply_count, np.NaN)

                    variabel=demand_df1.merge(supply[[supply_value]], left_index=True, right_index=True, how='left').fillna(0).drop(columns='samp')
                    variabel=variabel.loc[demand_locations][supply_value].to_numpy()

                    demand_df[supply_value]=variabel
                    
                    if options == 'N Total':
                        value_sum_supply=np.nansum(supply_mask, axis=1)
                        demand_df[supply_value+'_'+'N Total']=value_sum_supply
                        scaler=MinMaxScaler()
                        data1=[supply_value+'_'+'N Total']
                        data2=[''.join(data1+['_norm'])]
                        demand_df[data2] = scaler.fit_transform(demand_df[data1])
                        demand_df[supply_value+'_score']=demand_df[''.join(data1+['_norm'])]*score
                    # else:
                    #     scaler=MinMaxScaler()
                    #     data1=[supply_value+'_'+'N_Total']
                    #     data2=[''.join(data1+['_normi'])]
                    #     demand_df[data2] = scaler.fit_transform(demand_df[data1])
                    #     #data2=[''.join(data2+['_norm'])]
                    #     demand_df[''.join(data1+['_norm'])]=[abs(x-np.nanmax(demand_df[data2[0]])) for x in demand_df[data2[0]]]
                    #     demand_df[supply_value+'_score']=demand_df[''.join(data1+['_norm'])]*score

                    #     demand_df=demand_df.drop(columns=data2)
                    # 
                    elif options=='Mean Distance':
                        value_mean=np.nanmean(travel_mask, axis=1)
                        demand_df[supply_value+'_'+'Mean Distance']=value_mean

                    # if influence=='Negative':

                    #     scaler=MinMaxScaler()
                    #     data1=[supply_value+'_'+'Mean_Distance']
                    #     data2=[''.join(data1+['_norm'])]
                    #     demand_df[data2] = scaler.fit_transform(demand_df[data1])
                    #     demand_df[supply_value+'_score']=demand_df[''.join(data1+['_norm'])]*score
                    # else:
                        scaler=MinMaxScaler()
                        data1=[supply_value+'_'+'Mean Distance']
                        data2=[''.join(data1+['_normi'])]
                        demand_df[data2] = scaler.fit_transform(demand_df[data1])
                        #data2=[''.join(data2+['_norm'])]
                        demand_df[''.join(data1+['_norm'])]=[abs(x-np.nanmax(demand_df[data2[0]])) for x in demand_df[data2[0]]]
                        demand_df[supply_value+'_score']=demand_df[''.join(data1+['_norm'])]*score

                        demand_df=demand_df.drop(columns=data2)

                    else:
                        value_min=np.nanmin(travel_mask, axis=1)
                        demand_df[supply_value+'_'+'Nearest']=value_min

                    # if influence=='Negative':

                    #     scaler=MinMaxScaler()
                    #     data1=[supply_value+'_'+'Nearest']
                    #     data2=[''.join(data1+['_norm'])]
                    #     demand_df[data2] = scaler.fit_transform(demand_df[data1])
                    #     demand_df[supply_value+'_score']=demand_df[''.join(data1+['_norm'])]*score
                    # else:
                        scaler=MinMaxScaler()
                        data1=[supply_value+'_'+'Nearest']
                        data2=[''.join(data1+['_normi'])]
                        demand_df[data2] = scaler.fit_transform(demand_df[data1])
                        #data2=[''.join(data2+['_norm'])]
                        demand_df[''.join(data1+['_norm'])]=[abs(x-np.nanmax(demand_df[data2[0]])) for x in demand_df[data2[0]]]
                        demand_df[supply_value+'_score']=demand_df[''.join(data1+['_norm'])]*score

                        demand_df=demand_df.drop(columns=data2)

                else:
                    if options == 'No at all':
                        mask=(travel_np >0) & (travel_np <=mins)

                        travel_mask=np.where(mask, travel_np, np.NaN)
                        supply_mask=np.where(mask, supply_count, np.NaN)

                        variabel=demand_df1.merge(supply[[supply_value]], left_index=True, right_index=True, how='left').fillna(0).drop(columns='samp')
                        variabel=variabel.loc[demand_locations][supply_value].to_numpy()

                        demand_df[supply_value]=variabel

                        value_min=np.nanmin(travel_mask, axis=1)

                        v2=value_min > 0
                        v3=v2.astype(int)
                        thress=np.where(v3>0, np.NaN, 1)

                        demand_df[supply_value+'_'+'No at all']=thress

                        scaler=MinMaxScaler()
                        data1=[supply_value+'_'+'No at all']
                        data2=[''.join(data1+['_norm'])]
                        demand_df[data2] = scaler.fit_transform(demand_df[data1])
                        demand_df[supply_value+'_score']=demand_df[supply_value+'_'+'No at all']*score

                    else:
                        mask=(travel_np >mins) & (travel_np <=maxx)

                        travel_mask=np.where(mask, travel_np, np.NaN)
                        supply_mask=np.where(mask, supply_count, np.NaN)

                        variabel=demand_df1.merge(supply[[supply_value]], left_index=True, right_index=True, how='left').fillna(0).drop(columns='samp')
                        variabel=variabel.loc[demand_locations][supply_value].to_numpy()

                        demand_df[supply_value]=variabel

                        value_min=np.nanmin(travel_mask, axis=1)
                        demand_df[supply_value+'_'+options]=value_min

                        scaler=MinMaxScaler()
                        data1=[supply_value+'_'+options]
                        data2=[''.join(data1+['_norm'])]
                        demand_df[data2] = scaler.fit_transform(demand_df[data1])
                        demand_df[supply_value+'_score']=demand_df[''.join(data1+['_norm'])]*score



            else :

                var_n=eco_demo.loc[demand_locations, supply_value].to_numpy()

                mask=(var_n >=mins) & (var_n <=maxx)



                if options =='Min-Max':
                    min_max=np.where(mask, var_n, np.NaN)
                    demand_df[supply_value]=var_n
                    demand_df[supply_value+'_'+'Min-Max']=min_max

                    if influence=='Negative':

                        scaler=MinMaxScaler()
                        data1=[supply_value+'_'+'Min-Max']
                        data2=[''.join(data1+['_norm'])]
                        demand_df[data2] = scaler.fit_transform(demand_df[data1])
                        demand_df[supply_value+'_score']=demand_df[''.join(data1+['_norm'])]*score
                    else:
                        scaler=MinMaxScaler()
                        data1=[supply_value+'_'+'Min-Max']
                        data2=[''.join(data1+['_normi'])]
                        demand_df[data2] = scaler.fit_transform(demand_df[data1])
                        #data2=[''.join(data2+['_norm'])]
                        demand_df[''.join(data1+['_norm'])]=[abs(x-np.nanmax(demand_df[data2[0]])) for x in demand_df[data2[0]]]
                        demand_df[supply_value+'_score']=demand_df[''.join(data1+['_norm'])]*score

                        demand_df=demand_df.drop(columns=data2)


                elif options=='Threshold':
                    thress=mask.astype(int)
                    demand_df[supply_value]=var_n
                    demand_df[supply_value+'_'+'Threshold']=thress

                    scaler=MinMaxScaler()
                    data1=[supply_value+'_'+'Threshold']
                    data2=[''.join(data1+['_norm'])]
                    demand_df[data2] = scaler.fit_transform(demand_df[data1])
                    demand_df[supply_value+'_score']=demand_df[''.join(data1+['_norm'])]*score




        demand_df['total_score']=demand_df[sc].sum(axis=1)


        return demand_df

