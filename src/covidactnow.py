"""
############################################
# Set up paths to Modules & add to sys.path
############################################
"""
import sys
import numpy as np
from datetime import date
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

def clean():

    print("\n")

    """
    List the dataframes to be read in & Grab the most recent file
    """

    can = "./covid_act_now/covidactnow_*.csv"
    can = most_recent(can)
    print(f"\t{can}")


    """
    Get Covid Act Now data and Pre-Process to correct format
    """

    fips_loc = "/home/jennifp3/Documents/datasets/county_fips.csv"

    files = [can]
    has_fips =       [(False,"")]
    has_reportdate = [(True,"lastUpdatedDate","%Y-%m-%d")]

    # Read in data
    can, = preproc.load_dfs(files, has_fips, has_reportdate, skiprows=0)

    keep_cols = ["State","County","Metrics.Testpositivityratio",
                "Metrics.Casedensity","Metrics.Contacttracercapacityratio",
                "Metrics.Infectionrate","Metrics.Icuheadroomratio",
                "ReportDate"]
    can = preproc.keep_only(can,keep_cols)
    can.loc[:,"State"] = can["State"].str.upper()
    can.loc[:,"County"] = can["County"].str.title()

    # Update column names
    new_cols = {"Metrics.Testpositivityratio":"PositiveTestRate",
                "Metrics.Casedensity":"DailyNewCases",
                "Metrics.Contacttracercapacityratio":"TracersHired",
                "Metrics.Infectionrate":"InfectionRate",
                "Metrics.Icuheadroomratio":"IcuHeadroomUsed"}

    can.rename(columns=new_cols, inplace=True)

    # Process metrics (decimal places, percentages)
    can = can.replace(np.inf, np.nan)
    can.fillna(value=-999,axis=1,inplace=True)

    vals = can.loc[can.PositiveTestRate>=0, "PositiveTestRate"] * 100
    can.loc[can.PositiveTestRate>=0, "PositiveTestRate"] = vals
    can.loc[:,"PositiveTestRate"] = can["PositiveTestRate"].round(decimals=1)

    vals = can.loc[can.IcuHeadroomUsed>=0, "IcuHeadroomUsed"] * 100
    can.loc[can.IcuHeadroomUsed>=0, "IcuHeadroomUsed"] = vals
    can.loc[:,"IcuHeadroomUsed"] = can["IcuHeadroomUsed"].round(decimals=0)
    can.loc[:,"IcuHeadroomUsed"] = can["IcuHeadroomUsed"].astype(int)
    can.loc[can.IcuHeadroomUsed>100, "IcuHeadroomUsed"] = 100

    can.loc[:,"DailyNewCases"] = can["DailyNewCases"].round(decimals=1)
    can.loc[:,"InfectionRate"] = can["InfectionRate"].round(decimals=2)
    can.loc[:,"TracersHired"] = can["TracersHired"].astype(int)

    # Add missing columns
    can["Uploaded"] = True
    can["Url"] = f"https://covidactnow.org/us/al/county/"
    can["Url"] = can["Url"].str.cat(can["County"], sep="")

    # Add fips to dataframe
    can = preproc.add_fips(can, fips_loc, ["State","County"], ["stateiso","county"], level="county")
    can.loc[:,"State"] = can["State"].str.lower()
    can.loc[:,"County"] = can["County"].str.lower()
    can.loc[:,"County"] = can["County"].str.replace(" ", "_")

    # Reorder columns
    can = can[["State","County","Fips","ReportDate","DailyNewCases",
               "InfectionRate","PositiveTestRate","IcuHeadroomUsed",
               "TracersHired","Uploaded","Url"]]

    # Sort columns by Fips
    can.sort_values(by=["Fips"], inplace=True)

    # Save to selenium folder
    dayofweek = date.today()
    fname = f"/home/jennifp3/Documents/Python_scripts/selenium/covidactnow_county_{dayofweek}.csv"
    can.to_csv(fname, index=False)

    print(f"\t Formatted covidactnow_county_{dayofweek}.csv\n")

    return


if __name__ == "__main__":

    clean()
