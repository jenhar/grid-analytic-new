from configparser import LegacyInterpolation
#from msilib import MSIDBOPEN_DIRECT
#from tkinter import HORIZONTAL
#from turtle import left, right
import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import folium_static
import time
import numpy as np
import pandas as pd
import geopandas as gpd
from modul.analystModule import analystTeams

kams={'KOTA BOGOR':[-6.565816686684458,106.80355970214987], 'KOTA YOGYAKARTA':[-7.796605616724113,110.37810593427358],
 'KOTA CIREBON':[-6.705246775978466, 108.53214981398136]}

featkams={'household': {'min': 336.0, 'max': 17560.0, 'type': 'Demography'},
 'u10': {'min': 80.0, 'max': 3531.0, 'type': 'Demography'},
 'u15': {'min': 48.0, 'max': 3194.0, 'type': 'Demography'},
 'u20': {'min': 89.0, 'max': 4806.0, 'type': 'Demography'},
 'u25': {'min': 95.0, 'max': 4519.0, 'type': 'Demography'},
 'u30': {'min': 99.0, 'max': 4197.0, 'type': 'Demography'},
 'u35': {'min': 103.0, 'max': 4728.0, 'type': 'Demography'},
 'u40': {'min': 78.0, 'max': 4641.0, 'type': 'Demography'},
 'u45': {'min': 68.0, 'max': 4226.0, 'type': 'Demography'},
 'u50': {'min': 49.0, 'max': 3764.0, 'type': 'Demography'},
 'u55': {'min': 35.0, 'max': 2849.0, 'type': 'Demography'},
 'u60': {'min': 27.0, 'max': 2001.0, 'type': 'Demography'},
 'Landvalue': {'min': 17359.0, 'max': 8143500.0, 'type': 'Economic'},
 'Minimarket': {'type': 'POI'},
 'Railway Station': {'type': 'POI'},
 'Senior High School': {'type': 'POI'}}

st.set_page_config(page_title='GRID DASBOARD',
                    page_icon=":bar_chart:",
                    layout="wide")

#st.dataframe(df)

st.sidebar.header("Filter AREA: ")

area=st.sidebar.selectbox(
    "Select AREA",
    options=['<select>','KOTA BOGOR', 'KOTA YOGYAKARTA', 'KOTA CIREBON']
    )



loc=kams.get(area)

if loc:


    map_heatmap = folium.Map(location=loc, zoom_start=11)
    folium_static(map_heatmap)

st.sidebar.subheader("Inputs Parameter")

if st.sidebar.checkbox("Show advanced options"):
    par=st.sidebar.multiselect("Select Parameter", options=['household', 'u10', 'u15', 'u20', 'u25', 'u30', 'u35', 'u40', 'u45', 'u50', 'u55', 'u60', 'Landvalue', 'Minimarket', 'Railway Station', 'Senior High School'])
    var=[]
    skr=[]
    dsmin=[]
    dsmax=[]
    inf_skr=[]
    options_method=[]
    typess=[]

    for n, feature in enumerate(par):

        
        
        skoring=st.sidebar.number_input('Score '+ feature , 0,100, step=10)

        if featkams.get(feature)['type']=='Economici':
            positive_neg = st.sidebar.radio('Influence '+feature,('Positive', 'Negative'))
            min_selection, max_selection =st.sidebar.select_slider("Threshold " + feature, 
            options=['low', 'medium-low', 'medium-high', 'high'], value=('low', 'high'))

        elif featkams.get(feature)['type'] in ('Demography','Economic'):
            positive_neg = st.sidebar.radio('Influence '+feature,('Positive', 'Negative'))

            minn=int(featkams.get(feature)['min'])
            maxx=int(featkams.get(feature)['max'])

            min_selection, max_selection = st.sidebar.slider(feature, min_value=minn, max_value=maxx, value=[minn,maxx], step=100)
            options_method.append('Min-Max')

            if st.sidebar.checkbox("Advanced Option Used " +feature+" as Threshold"):

                feature_power = 'Threshold'
                st.sidebar.write('Influence Positive Or Negative will be ignored')
                st.sidebar.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
                options_method[n]=feature_power


            
        else:
            positive_neg = st.sidebar.radio('Influence '+feature,('Positive', 'Negative'))
            if positive_neg =='Positive':
                min_selection, max_selection = st.sidebar.slider("Threshold "+ feature, min_value=0, max_value=10000, value=[0,10000], step=1000)
                options_method.append('Nearest')
                if st.sidebar.checkbox("POI advanced "+feature):
                    feature_power = st.sidebar.radio('Power '+feature,('Nearest', 'N Total', 'Mean Distance'))
                    st.sidebar.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
                    options_method[n]=feature_power
            else:
                negative = st.sidebar.radio('Influence '+feature,('No at all', 'if any'))
                options_method.append(negative)
                st.sidebar.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
                

                if negative=='No at all':
                    min_slct = st.sidebar.slider("Minimum Distance " + feature,0,10000, step=1000)

                    min_selection=min_slct
                    max_selection=np.NaN
                    

                elif negative=='if any':
                    min_selection, max_selection = st.sidebar.slider("Threshold Distance"+ feature, min_value=0, max_value=10000, value=[0,10000], step=1000)

        typess.append(featkams.get(feature)['type'])


        var.append(feature)
        skr.append(skoring)
        dsmin.append(min_selection)
        dsmax.append(max_selection)
        inf_skr.append(positive_neg)

        bobot=sum(skr)

    
    df=pd.DataFrame({'Parameter':var,'type':typess,'Score':skr,'Influence':inf_skr,'Options':options_method,'Min_Threshold':dsmin,'Max_Threshold':dsmax})

    st.write('Table Scoring')

    st.dataframe(df)

    if sum(df.Score) <=99:
        st.sidebar.warning('Total Score Must be 100!', icon="⚠️")

    opt=['total_score']
        
    for x,x1 in zip(df['Parameter'],df['Options']):
        opt.append(x)
        opt.append(x+'_score') 
        opt.append(x+'_'+x1)

    col=st.sidebar.multiselect("Parameter To Show",
    options=opt )
    
        
    submit=st.sidebar.button('ANALYZE')

    if submit:

        with st.spinner('Wait for it...'):

            chi_cost=pd.read_parquet('data/grid_cost.parquet')
            df2=pd.read_parquet('data/supply.parquet')
            bogor_pop=gpd.read_file('data/bogor_grd.geojson')
            eco_demo=pd.read_parquet('data/eco_demo.parquet')
            #df=pd.read_parquet('input_file.parquet')
            #df.to_parquet("input_file.parquet")
            #time.sleep(10)
            
            demand_df = analystTeams.gridAnalyst(bogor_pop, df2,chi_cost, eco_demo, df)

            lat,lon=kams.get(area)
            pop=demand_df.reset_index()
            lga_json = pop.__geo_interface__

            st.success('Done!')

            for cols in col:



                fig = px.choropleth_mapbox(pop, geojson=lga_json, color=cols, hover_name='gid',
                                            locations="gid", featureidkey="properties.gid",
                                            center={"lat": lat, "lon": lon},
                                            color_continuous_scale='viridis_r',
                                            mapbox_style="carto-positron", zoom=9,width=900, height=700,
                                            opacity=0.7,
                                            title=cols)
                st.plotly_chart(fig)

            demand_dfc=demand_df.copy()
            demand_dfc=demand_dfc.drop(columns='geometry')

            st.dataframe(demand_dfc.head(50))

            

        
st.sidebar.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)









# df = px.data.election()
# geojson = px.data.election_geojson()

# fig = px.choropleth_mapbox(df, geojson=geojson, color="Bergeron",
#                            locations="district", featureidkey="properties.district",
#                            center={"lat": 45.5517, "lon": -73.7073},
#                            mapbox_style="carto-positron", zoom=9)


# st.plotly_chart(fig)





# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
