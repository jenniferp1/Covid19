"""
############################################
# Set up paths to Modules & add to sys.path
############################################
"""
import sys
from os import scandir


modules = "/home/jennifp3/Documents/Python_scripts/Modules"
excludes = ["__pycache__",".ipynb_checkpoints"] # list of subdirs to ignore
dirls = [f.path for f in scandir(modules) if f.is_dir()]
includes = [d for d in dirls if not any(x in d for x in excludes)]
for d in includes:
    sys.path.insert(0,d)
sys.path.insert(0,modules)

""" IMPORT STATEMENTS """
from readin import most_recent
import preproc

import pandas as pd


""" FUNCTIONS """

def get_counties():

    print("\n")

    """
    List the dataframes to be read in & Grab the most recent file
    """

    covid_act_now = "/home/jennifp3/Documents/Python_scripts/selenium/covidactnow_county*.csv"
    covid_act_now = most_recent(covid_act_now)
    print(f"\t{covid_act_now}")

    cdph = "./california/CaliforniaCountyData*.csv"
    cdph = most_recent(cdph)
    print(f"\t{cdph}")

    """
    PreProcess CDPH dataset
    """

    fips_loc = "/home/jennifp3/Documents/datasets/county_fips.csv"

    files = [cdph]
    has_fips =       [(False,"")]
    has_reportdate = [(True,"Date of Tier Assessment","%Y-%m-%d %H:%M:%S")]

    # Get number of non-header rows to skip over
    skiprows = pd.read_csv(cdph)

    for i in range(len(skiprows.index)-1):
        if skiprows.iloc[i,0] == "County":
            skiprows = i + 1
            break

    # Read in data skipping non-header rows
    cdph, = preproc.load_dfs(files, has_fips, has_reportdate, skiprows=skiprows)

    for col in cdph.columns.to_list():
        if col.startswith("TestPositivityExclPri"):
            col_name = col
            break

    keep_cols = ["County","ReportDate",
                col_name,]
    cdph = preproc.keep_only(cdph,keep_cols)
    cdph["State"] = "California"
    new_cols = {col_name:"Positivity",}
    cdph.rename(columns=new_cols, inplace=True)
    # https://stackoverflow.com/questions/16176996/keep-only-date-part-when-using-pandas-to-datetime
    cdph["ReportDate"] = cdph["ReportDate"].dt.date

    # Drop end rows without valid data (contains footnotes)
    cdph.dropna(how='any',inplace=True)

    # Remove * from county names
    cdph["County"] = cdph["County"].str.replace("*", "")

    # Remove ^ from county names
    cdph["County"] = cdph["County"].str.replace("^", "")

    # Add 'County' to end of each county so can add fips
    cdph = cdph.assign(County = cdph.County + " County")

    # Add fips to dataframe
    cdph = preproc.add_fips(cdph, fips_loc, ["State","County"], ["state","county"], level="county")

    # Round Positivity to 2 decimals
    cdph.loc[:, "Positivity"] = cdph["Positivity"].round(decimals=2)

    """
    Get Covid Act Now data
    """

    can = pd.read_csv(covid_act_now, dtype={"Fips":str})


    """
    Replace PositiveTestRate with cdph Positivity
    """

    df = pd.merge(can[can.State=="ca"],
                  cdph[["Fips", "ReportDate", "Positivity"]],
                  left_on=["Fips"],
                  right_on=["Fips"],
                  how="left")

    df.drop(["ReportDate_x", "PositiveTestRate"], axis=1, inplace=True)

    new_cols = {"Positivity":"PositiveTestRate",
                "ReportDate_y":"ReportDate"}

    df.rename(columns=new_cols, inplace=True)

    cols = ["State", "County", "Fips", "ReportDate", "DailyNewCases",
    	    "InfectionRate", "PositiveTestRate", "IcuHeadroomUsed",
            "TracersHired", "Uploaded",	"Url"]

    df = df[cols]

    can = can[can.State!="ca"]
    can = can.append(df, ignore_index=True)
    can.sort_values(by=["Fips"], inplace=True)

    fname = "/home/jennifp3/Documents/Python_scripts/selenium/covidactnow_ca_countyPositivity.csv"
    can.to_csv(fname, index=False)

    print(f"\n\tDataFrame with California county positivity saved to: \n\t   {fname}\n")

    return


if __name__ == "__main__":

    get_counties()
