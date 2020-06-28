import altair as alt
from vega_datasets import data
import numpy as np
# import geopandas as gpd

import pandas as pd
import pprint as pt

title = 'Unemployment %, Mar-20'
color_scheme = 'inferno'
tick_count = 6


source = pd.read_csv('input.csv', usecols=['State FIPS', 'County FIPS', 'rate', 'Period'], dtype={'State FIPS':np.int, 'County FIPS':str, 'Period':str, 'rate':np.float64})
# new_header = source.iloc[0] #grab the first row for the header
# source = source[1:] #take the data less the header row
# source.columns = new_header
keys = list(source.columns.values)
print('Columns: '+str(keys))
source['State FIPS'] = source['State FIPS'].astype(str)
# source['id2'] = source['id2'].astype(str)
source['id'] = source['State FIPS']+source['County FIPS']

# source['rate'] = pd.to_numeric(source['rate'])
pt.pprint(source['id'])

# source  = data.unemployment.url


counties = alt.topo_feature('file:///us-10m.json', 'counties')
# counties = alt.Data(url='us-county-boundaries.geojson', format=alt.DataFormat(property='features',type='json'))
# source = data.unemployment.url

states = alt.topo_feature(data.us_10m.url, 'states')
capitals = data.us_state_capitals.url

# hover = alt.selection(type='single', on='mouseover', nearest=False, fields=['lat', 'lon'])

chart = alt.Chart(counties).mark_geoshape().encode(
    color=alt.Color('rate:Q', scale=alt.Scale(scheme=color_scheme), legend=alt.Legend(title=title, tickCount=tick_count)),
    tooltip='id:Q'
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(source[source['Period']=='Apr-19'], 'id', ['rate'])
    # from_=alt.LookupData(source, 'id', ['rate'])
).project(
    type='albersUsa'
).properties(
    width=1000,
    height=600
)

base = alt.Chart(capitals).encode(
    longitude='lon:Q',
    latitude='lat:Q',
)

text = base.mark_text(dx=7, align='left').encode(
    alt.Text('city', type='nominal'),
    color=alt.value('green'),
    opacity=alt.value(0.8)#alt.condition(~hover, alt.value(0), alt.value(1))
)

points = base.mark_point().encode(
    color=alt.value('green'),
    size=alt.value(3)#alt.condition(~hover, alt.value(5), alt.value(15))
)

chart = chart + points

chart.configure_legend(
    # gradientLength=550,
    # gradientThickness=30,
    gradientOpacity=0.8,
    gradientDirection='horizontal',
    # titleAlign='center',
    gradientLength=1000,
    orient='bottom',
    titleFontSize=16,
    titleAnchor='middle',
).configure_view(strokeWidth=0)

from altair_saver import save
save(chart, 'counties.html')
