import glob
import os, re
import pandas as pd
import numpy as np
import datetime
from datetime import datetime, date

from urllib.request import urlopen
import json
import plotly.express as px
import plotly.graph_objects as go

def get_today():
    now = date.today()
    now = now.strftime("%Y-%m-%d")
    return now

def most_recent(filedir):
    file = max(glob.iglob(filedir),key=os.path.getmtime)
    return file

def get_colors(df, colors, cat_options):

    scheme = []
    categories = df.unique()

    if len(categories) > len(colors):
        print("Error in method get_colors: More categories than color options")
        print("Exiting...\n")
        exit()

    if len(cat_options) != len(colors):
        print("Error in method get_colors: Categories options doesn't match color options")
        print("Exiting...\n")
        exit()

    for i in range(len(cat_options)):
        if cat_options[i] in categories:
            scheme.append(colors[i])

    return scheme


def load_dfs(files, has_fips, has_reportdate):
    """
    has_fips: tuple (Boolean, Header), indicates if the csv already has fips and
        if so what the header name is for the fips column

    has_reportdate: tuple (Boolean, Header, Date format), indicates if csv has report date
        and if so header name of the column and the format of the date
    """

    dfs = []

    if len(files) != len(has_fips) and len(files) != len(has_reportdate):
        print("Error in loading csvs to DataFrames.  files and has_fips differ in length.")
        print("Exiting...\n")
        exit()

    for i in range(len(files)):
        if has_fips[i][0] and has_reportdate[i][0]:
            df = pd.read_csv(files[i], dtype={has_fips[i][1]:str})
            df[has_reportdate[i][1]] = pd.to_datetime(df[has_reportdate[i][1]], format=has_reportdate[i][2])
            df.rename(columns={has_reportdate[i][1]:"Report Date", has_fips[i][1]:"Fips"}, inplace=True)
        elif has_fips[i][0]:
            df = pd.read_csv(files[i], dtype={has_fips[i][1]:str})
            df.rename(columns={has_fips[i][1]:"Fips"}, inplace=True)
            df = add_reportdate(df, files[i])
        elif has_reportdate[i][0]:
            df = pd.read_csv(files[i])
            df[has_reportdate[i][1]] = pd.to_datetime(df[has_reportdate[i][1]], format=has_reportdate[i][2])
            df.rename(columns={has_reportdate[i][1]:"Report Date"}, inplace=True)
        else:
            df = pd.read_csv(files[i])
            df = add_reportdate(df, files[i])
        df = fix_headers(df, df.columns)
        dfs.append(df)

    print("DataFrames loaded to memory\n")

    return dfs


def add_fips(df, fips_loc, left, right, level):

    if (level != "state") and (level != "county"):
        print("Error: set level to 'state' or 'county'")
        print("Exiting....\n")
        exit()

    fips = pd.read_csv(fips_loc, dtype={"fips":str})
    fips.rename(columns={"fips":"Fips"}, inplace=True)
    if level == "state":
        fips = fips[~fips.county.notnull()]

    df = pd.merge(df,
                  fips[["Fips",right]],
                  left_on=left,
                  right_on=right,
                  how="left")
    return df


def add_state_names(df, abbr_loc, left, right):

    abbr = pd.read_csv(abbr_loc)
    df[left] = df[left].str.upper()
    df = pd.merge(df,
                  abbr,
                  left_on=left,
                  right_on=right,
                  how="left")

    return df


def add_regions(df, regions_loc, left, right):

    regions = pd.read_csv(regions_loc, dtype={"StateFips":str})
    df = pd.merge(df,
                  regions,
                  left_on=left,
                  right_on=right,
                  how="left")
    return df


def keep_only(df, cols):
    return df[cols]


def fix_headers(df, cols):

    newcols = [header.title() for header in cols]
    newcols = [header.replace(" ","") for header in newcols]
    df.columns = newcols
    return df


def add_reportdate(df, filename):

    reportdate = re.findall(r"(\d{4}-\d{2}-\d{2})", filename)[0]
    df["Report Date"] = reportdate
    df["Report Date"] = pd.to_datetime(df["Report Date"], format="%Y-%m-%d")
    return df


def load_county_geojson():

    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
        counties = json.load(response)

    # update values for Kusilvak
    counties["features"][74]["properties"]["COUNTY"] = '158'
    counties["features"][74]["properties"]["NAME"] = 'Kusilvak'
    counties["features"][74]["id"] = '02158'

    # update values for Oglala Lakota
    counties["features"][1581]["properties"]["COUNTY"] = '102'
    counties["features"][1581]["properties"]["NAME"] = 'Oglala Lakota'
    counties["features"][1581]["id"] = '46102'

    return counties

def load_state_geojson():

    with urlopen('https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json') as response:
        states = json.load(response)

    return states


def state_map(df):

    columns = ["ReportDate", "State", "Fips", "Positivity", "PositivityIs"]

    return

if __name__ == "__main__":

    print("\n")

    """
    List the dataframes to be read in & Grab the most recent file
    """

    covid_exit_strat = "./covid_exit_strategy_testing/*.csv"
    covid_exit_strat = most_recent(covid_exit_strat)
    print(covid_exit_strat)

    virginia = "./virginia/county/*.csv"
    virginia = most_recent(virginia)
    print(virginia)

    minnesota = "./minnesota/*.csv"
    minnesota = most_recent(minnesota)
    print(minnesota)

    # covid_act_now = "/home/jennifp3/Documents/Python_scripts/selenium/covidactnow_county*.csv"
    covid_act_now = "/home/jennifp3/Documents/Python_scripts/selenium/covidactnow_ca_countyPositivity.csv"
    covid_act_now = most_recent(covid_act_now)
    print(covid_act_now)

    covid_tracking_proj = "./covid_tracking_proj_hist/*.csv"
    covid_tracking_proj = most_recent(covid_tracking_proj)
    print(covid_tracking_proj)

    print("\n")

    """
    Load dataframes
    """

    fips_loc = "/home/jennifp3/Documents/datasets/county_fips.csv"
    state_abbr = "/home/jennifp3/Documents/datasets/state_abbrv.csv"
    regions_loc = "/home/jennifp3/Documents/datasets/censusregions.csv"

    files = [covid_exit_strat, virginia, minnesota, covid_act_now, covid_tracking_proj]
    has_fips =       [(False,""), (True,"CountyFIPS"),       (True,"fips"),(True,"Fips"),       (True,"fips")]
    has_reportdate = [(False,"",""), (True,"lab_report_date","%Y-%m-%d"),  (False,"",""),   (True,"ReportDate","%Y-%m-%d"), (True,"date","%Y%m%d")]

    ces, va, mn, can, ctp = load_dfs(files, has_fips, has_reportdate)


    """
    Preprocessing: Covid Exit Strategy Testing
    """

    ces = add_fips(ces, fips_loc, "State", "state", level="state")

    ces_cols = ["State", 'PositivityIs', 'Positivity-13', 'Positivity-12', 'Positivity-11',
       'Positivity-10', 'Positivity-09', 'Positivity-08', 'Positivity-07',
       'Positivity-06', 'Positivity-05', 'Positivity-04', 'Positivity-03',
       'Positivity-02', 'Positivity-01', 'Positivity-00', 'Positivity', 'Fips', 'ReportDate']

    ces = keep_only(ces, ces_cols)
    ces["PositivityIs"] = ces["PositivityIs"].str.extract(pat = "([a-zA-Z]+)")
    ces = ces[["ReportDate", "Fips", "State", "Positivity",
       "PositivityIs",'Positivity-13', 'Positivity-12',
       'Positivity-11', 'Positivity-10', 'Positivity-09', 'Positivity-08',
       'Positivity-07', 'Positivity-06', 'Positivity-05', 'Positivity-04',
       'Positivity-03', 'Positivity-02', 'Positivity-01', 'Positivity-00']]

    ces = ces[~ces.Fips.isnull()]


    """
    Preprocessing: Virginia
    """

    va["State"] = "Virginia"
    va_cols = ['ReportDate', 'Fips', 'State', 'Citycounty', 'Positivity_Pcr_7Day']
    va = keep_only(va,va_cols)
    va.rename(columns={"Positivity_Pcr_7Day":"Positivity", "Citycounty":"County"}, inplace=True)
    va["Positivity"] = va["Positivity"]*100
    va["Positivity"] = va["Positivity"].round(2)
    va.sort_values(by=["ReportDate","County"], ascending=False, ignore_index=True, inplace=True)

    latest_date = va["ReportDate"][0]
    va = va[va.ReportDate==latest_date]

    """
    Preprocessing: Minnesota
    """

    mn_cols = ['ReportDate', 'Fips', 'State', 'County', 'Positive']
    mn = keep_only(mn,mn_cols)
    mn.rename(columns={"Positive":"Positivity"}, inplace=True)

    """
    Preprocessing: Covid Act Now
    """

    can = add_state_names(can, state_abbr, "State", "Abbreviation")
    can_cols = ['ReportDate', 'Fips', 'State_y', 'County', 'Positivetestrate']
    can = keep_only(can,can_cols)
    # can["County"] = can["County"].str.extract(pat = "(^.*?(?=_))")
    can["County"] = can["County"].str.title()
    can["County"] = can["County"].replace("_County","",regex=True)
    can["County"] = can["County"].replace("Mc_","Mc",regex=True)
    can["County"] = can["County"].replace("De_","De",regex=True)
    can["County"] = can["County"].replace("_"," ",regex=True)
    can.rename(columns={"State_y":"State","Positivetestrate":"Positivity"}, inplace=True)
    # can.to_csv("after.csv",index=False)

    """
    Preprocessing: Covid Tracking Project
    """

    ctp = add_state_names(ctp, state_abbr, "State", "Abbreviation")
    ctp = add_fips(ctp, fips_loc, "State_y", "state", level="state")
    ctp = add_regions(ctp, regions_loc, "Fips_y", "StateFips")

    ctp_cols = ['ReportDate', 'Fips_y', 'State_y', 'CensusRegionName', 'Positiveincrease', 'Totaltestresultsincrease']
    ctp = keep_only(ctp, ctp_cols)
    ctp.rename(columns={"Fips_y":"Fips", "State_y":"State",
                        'Positiveincrease':"PositiveIncr",
                        'Totaltestresultsincrease':"TotTestIncr"}, inplace=True)
    ctp = ctp[~ctp.Fips.isnull()]
    ctp.reset_index(drop=True, inplace=True)

    # https://stackoverflow.com/questions/45372187/python-pandas-replace-value-if-previous-value-is-same-as-next-value #
    # ctp.loc[ctp.PositiveIncr.shift(0) < 0, "PositiveIncr"] = ctp.groupby(by="State")["PositiveIncr"].transform(lambda x: x.shift(1))
    ctp[["PositiveIncr","TotTestIncr"]] = ctp[["PositiveIncr","TotTestIncr"]].replace({0:np.nan,0:np.nan})
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/missing_data.html#interpolation #
    ctp["PositiveIncr"] = ctp.groupby(by="State")["PositiveIncr"].transform(lambda x: x.interpolate(method="values"))
    ctp["PositiveIncr"] = ctp["PositiveIncr"].round()
    ctp["TotTestIncr"] = ctp.groupby(by="State")["TotTestIncr"].transform(lambda x: x.interpolate(method="values"))
    ctp["TotTestIncr"] = ctp["TotTestIncr"].round()

    ctp.loc[ctp.TotTestIncr.shift(0) < 0, "TotTestIncr"] = ctp.groupby(by="State")["TotTestIncr"].transform(lambda x: (x.shift(1)+x.shift(-1))/2.0)
    ctp["TotTestIncr"] = ctp["TotTestIncr"].round()

    ctp["Positivity"] = (ctp["PositiveIncr"]/ctp["TotTestIncr"]) * 100

    ctp.sort_values(by=["State", "ReportDate"], ascending=(True,True), inplace=True)
    ctp["Positivity7Day"] = ctp.groupby(by="State")["Positivity"].transform(lambda x: x.rolling(7, 1).mean())

    ctp.sort_values(by=["CensusRegionName","ReportDate"], ascending=(True,True), inplace=True)
    # ctp["PositivityRegion"] = ctp.groupby(["CensusRegionName","ReportDate"])["Positivity"].transform(lambda x: x.mean())
    # ctp["PositivityRegion7Day"] = ctp.groupby(["CensusRegionName","State"])["PositivityRegion"].transform(lambda x: x.rolling(7, 1).mean())
    ctp["PositiveIncrRegion"] = ctp.groupby(["CensusRegionName","ReportDate"])["PositiveIncr"].transform(lambda x: x.sum())
    ctp["TotTestIncrRegion"] = ctp.groupby(["CensusRegionName","ReportDate"])["TotTestIncr"].transform(lambda x: x.sum())
    ctp["PositivityRegion"] = (ctp["PositiveIncrRegion"]/ctp["TotTestIncrRegion"]) * 100
    ctp["Positivity7DayRegion"] = ctp.groupby(["CensusRegionName","State"])["PositivityRegion"].transform(lambda x: x.rolling(7, 1).mean())

    ctp.sort_values(by=["ReportDate","State"], ascending=(False,True), inplace=True)
    ctp["Positivity"] = ctp["Positivity"].round(2)
    ctp["Positivity7Day"] = ctp["Positivity7Day"].round(2)
    ctp["PositivityRegion"] = ctp["PositivityRegion"].round(2)
    ctp["Positivity7DayRegion"] = ctp["Positivity7DayRegion"].round(2)

    ctp = ctp[['ReportDate', 'Fips', 'State', 'CensusRegionName', 'PositiveIncr', 'PositiveIncrRegion',
       'TotTestIncr', 'TotTestIncrRegion', 'Positivity', 'Positivity7Day', 'PositivityRegion',
       'Positivity7DayRegion']]


    """
    Combine Virginia, Minnesota, Covid Act Now
    """

    counties_all = can[(can.State != "Virginia") & (can.State != "Minnesota")]
    counties_all = counties_all.append(va, ignore_index=True)
    counties_all = counties_all.append(mn, ignore_index=True)

    counties_all.loc[counties_all.Positivity < 0,"PosTestCategory"] = "Unknown"
    counties_all.loc[(counties_all.Positivity >= 0) & (counties_all.Positivity < 5),"PosTestCategory"] = "Low (< 5%)"
    counties_all.loc[(counties_all.Positivity >= 5) & (counties_all.Positivity < 10),"PosTestCategory"] = "Moderate (5 - 10%)"
    counties_all.loc[(counties_all.Positivity >= 10) &(counties_all.Positivity < 20),"PosTestCategory"] = "High (10 - 20%)"
    counties_all.loc[(counties_all.Positivity >= 20),"PosTestCategory"] = "Extreme (> 20%)"
    # counties_all[["State","County","Positivity","PosTestCategory"]]

    counties_all.sort_values(by="Positivity", ascending=False, inplace=True)
    counties_all["ReportDate"] = counties_all["ReportDate"].dt.strftime("%Y-%m-%d")
    dt = counties_all["ReportDate"].max()
    dt = datetime.strptime(dt, "%Y-%m-%d")
    month = datetime.strptime(str(dt.month), "%m")
    month = month.strftime("%B")
    fulldate = f"{month} {dt.day}, {dt.year}"

    """
    Plot county positivity
    """

    county_fips = load_county_geojson()

    # color_scheme = ["#f03b20", "#feb24c", "#ffeda0", "#2ca25f", "#f0f0f0"]
    # color_scheme = ["#d55e00", "#cc72b2", "#f0e442", "#009e73", "#f0f0f0"]
    color_scheme = ["#ca0020", "#f4a582", "#92c5de", "#0571b0", "#f0f0f0"]
    cat_options = ["Extreme (> 20%)", "High (10 - 20%)", "Moderate (5 - 10%)", "Low (< 5%)", "Unknown"]

    color_scheme = get_colors(counties_all["PosTestCategory"], color_scheme, cat_options)


    fig = px.choropleth_mapbox(counties_all, geojson=county_fips, locations="Fips", color="PosTestCategory",
                           color_discrete_sequence=color_scheme,
                           mapbox_style="carto-positron",
#                            mapbox_style = "albers usa",
                           zoom=3, center = {"lat": 37.0902, "lon": -95.7129},
                           labels={'Positivity':'Positive Test Rate (%) ',
                                   'PosTestCategory' : 'Category Ranking',
                                   'ReportDate' : 'Report Date'},
                           hover_name="County",
                           hover_data={'Fips':False,
                                       'State':True,
                                       'ReportDate':True,
                                       'Positivity':': .1f',
                                       'PosTestCategory':False,
                            }
                          )
    title = f"Positivity by County (Updated on: {fulldate})" + "<br>" + "(Average rates, see data definitions for details)"
    fig.update_layout(margin={"r":0,"t":60,"l":0,"b":0}, title=title, legend_orientation="h")

    today = get_today()

    fig.write_html(f"./county_positivity_{today}.html")

    """
    Plot state positivity
    """

    state_fips = load_state_geojson()

    ces.loc[ces.Positivity < 0,"PosTestCategory"] = "Unknown"
    ces.loc[(ces.Positivity >= 0) & (ces.Positivity < 5),"PosTestCategory"] = "Low (< 5%)"
    ces.loc[(ces.Positivity >= 5) & (ces.Positivity < 10),"PosTestCategory"] = "Moderate (5 - 10%)"
    ces.loc[(ces.Positivity >= 10) &(ces.Positivity < 20),"PosTestCategory"] = "High (10 - 20%)"
    ces.loc[(ces.Positivity >= 20),"PosTestCategory"] = "Extreme (> 20%)"


    ces.sort_values(by="Positivity", ascending=False, inplace=True)
    ces["ReportDate"] = ces["ReportDate"].dt.strftime("%Y-%m-%d")
    dt = ces["ReportDate"].max()
    dt = datetime.strptime(dt, "%Y-%m-%d")
    month = datetime.strptime(str(dt.month), "%m")
    month = month.strftime("%B")
    fulldate = f"{month} {dt.day}, {dt.year}"


    color_scheme = ["#ca0020", "#f4a582", "#92c5de", "#0571b0", "#f0f0f0"]
    cat_options = ["Extreme (> 20%)", "High (10 - 20%)", "Moderate (5 - 10%)", "Low (< 5%)", "Unknown"]

    color_scheme = get_colors(ces["PosTestCategory"], color_scheme, cat_options)

    fig = px.choropleth_mapbox(ces, geojson=state_fips, locations="Fips", color="PosTestCategory",
                           color_discrete_sequence=color_scheme,
                           mapbox_style="carto-positron",
#                            mapbox_style = "albers usa",
                           zoom=3, center = {"lat": 37.0902, "lon": -95.7129},
                           labels={'Positivity':'Positive Test Rate (%) ',
                                   'PosTestCategory' : 'Category Ranking',
                                   'ReportDate' : 'Report Date',
                                   'PositivityIs' : '2-Week Positivity Trend is'},
                           hover_name="State",
                           hover_data={'Fips':False,
                                       'State':False,
                                       'ReportDate':True,
                                       'PositivityIs':True,
                                       'Positivity':': .1f',
                                       'PosTestCategory':False,
                            }
                          )

    title = f"Positivity by State (Updated on: {fulldate})" + "<br>" + "(7-Day Rollling Avg.)"
    fig.update_layout(margin={"r":0,"t":60,"l":0,"b":0}, title=title, legend_orientation="h")

    today = get_today()

    fig.write_html(f"./state_positivity_{today}.html")

    """
    Plot bar chart for states between 10% and 20%
    """

    df = ces[ces.ReportDate==max(ces.ReportDate)]
    df = df[["ReportDate","State","Positivity","PositivityIs", "PosTestCategory"]]
    df = df[df.PosTestCategory=="High (10 - 20%)"]
    df.sort_values(by="Positivity", ascending=True, inplace=True)
    df["text"] = df["Positivity"].astype(str) + "% (" + df["PositivityIs"] +")"
    incr = df[df.PositivityIs=="Increasing"]
    decr = df[df.PositivityIs=="Decreasing"]
    flat = df[df.PositivityIs=="Flat"]

    fig = go.Figure()

    fig.add_trace(go.Bar(
                x=decr["Positivity"],
                y=decr["State"],
                text=decr["text"],
                hovertemplate =
                    '<extra></extra>'+
                    '<br>Positivity: %{x:.1f}%'+
                    '<br>State: %{y}<br>',
                textposition='auto',
                # marker_color='rgb(44,123,182)',
                marker_color='rgb(244,165,130)',
                name = "Decreasing",
                orientation='h'))

    fig.add_trace(go.Bar(
                x=flat["Positivity"],
                y=flat["State"],
                text=flat["text"],
                hovertemplate =
                    '<extra></extra>'+
                    '<br>Positivity: %{x:.1f}%'+
                    '<br>State: %{y}<br>',
                textposition='auto',
                # marker_color='rgb(253,174,97)',
                marker_color='rgb(244,165,130)',
                name = "Flat",
                orientation='h'))

    fig.add_trace(go.Bar(
                x=incr["Positivity"],
                y=incr["State"],
                text=incr["text"],
                hovertemplate =
                    '<extra></extra>'+
                    '<br>Positivity: %{x:.1f}%'+
                    '<br>State: %{y}<br>',
                textposition='auto',
                # marker_color='rgb(215,25,28)',
                marker_color='rgb(244,165,130)',
                name = "Increasing",
                orientation='h'))

    fig.update_xaxes(title="Positivity (%)")

    title = "<b>States with Positivity Rates between 10 and 20 Percent</b>" + f" (Updated on: {fulldate})" + "<br>" + "(7-Day Rolling Avg.)"
    fig.update_layout(title=title,
                     title_x = 0.5, title_y=0.94)

    fig.update_layout(yaxis={'categoryorder':'total ascending'}) # Comment for separation by category

    fig.update_layout(showlegend=False,
        title=dict(font=dict(
            family="Courier New, monospace",
            size=20,
            )
        ),

        font=dict(
        family="Courier New, monospace",
        size=16,
    ))

    today = get_today()

    fig.write_html(f"./state_high_positivity_{today}.html")



    """
    Time series: Months
    """

    print(ctp.head())
    # groups = ctp.groupby(["CensusRegionName","ReportDate"])
    # print(groups.groups.keys())
    # print(groups.get_group(("West", '2020-09-02 00:00:00')))
    ctp.to_csv("ctp_after.csv",index=False)

    ces.to_csv("ces_after.csv", index=False)
