"""
############################################
# Set up paths to Modules & add to sys.path
############################################
"""
import sys
from os import scandir

master = "/home/jennifp3/Documents/Python_scripts/Modules/filefetch_master"
excludes = ["__pycache__","history","doc","setup",".ipynb_checkpoints"] # list of subdirs to ignore
dirls = [f.path for f in scandir(master) if f.is_dir()]
includes = [d for d in dirls if not any(x in d for x in excludes)]
for d in includes:
    sys.path.insert(0,d)

modules = "/home/jennifp3/Documents/Python_scripts/Modules"
excludes = ["__pycache__",".ipynb_checkpoints"] # list of subdirs to ignore
dirls = [f.path for f in scandir(modules) if f.is_dir()]
includes = [d for d in dirls if not any(x in d for x in excludes)]
for d in includes:
    sys.path.insert(0,d)
sys.path.insert(0,modules)

""" IMPORT STATEMENTS """
from filefetch.FileFetch import FileFetch
import vdh, cdph, covidactnow

import pandas as pd
from datetime import date
import calendar


"""
######################
# Daily upload code  #
######################
"""

rt_file = ["../url_filefetch.yml", "rt_live"]
tat_file = ["../url_filefetch.yml", "test_and_trace"]
can_file = ["../url_filefetch.yml", "covid_act_now"]
ces_file = ["../url_filefetch.yml", "covid_exit_strat_testing"]
ces_file2 = ["../url_filefetch.yml", "covid_exit_strat_healthcare"]
ces_file3 = ["../url_filefetch.yml", "covid_exit_strat_spread"]
ctp = ["../url_filefetch.yml", "covid_tracking_proj_race"]
ctph = ["../url_filefetch.yml", "covid_tracking_proj_hist"]
mn = ["../url_filefetch.yml", "minnesota"]
va = ["../url_filefetch.yml", "virginia"]
hhs = ["../url_filefetch.yml", "hhs_icu"]
poli = ["../url_filefetch.yml", "COVID19StatePolicy"]
kff = ["../url_filefetch.yml", "kff"]
ca = ["../url_filefetch.yml", "california"]

files = [rt_file, tat_file, can_file, ces_file, ces_file2, ces_file3, ctp, ctph,
        mn, va, hhs, poli, kff, ca]

fnames = [
    "rtlive",
    "testandtrace",
    "covidactnow",
    "covidexitstrategy",
    "covidexitstrategy",
    "covidexitstrategy",
    "covidtrackproj",
    "covidtrackproj",
    "MinnesotaCountyTestData",
    "VirginiaHealthDistrictTestData",
    ["hhs_table1", "hhs_table2", "hhs_table3"],
    "StatePolicy",
    "kff",
    "CaliforniaCountyData",
]

fpaths = [
    "./rt_live",
    "./test_trace",
    "./covid_act_now",
    "./covid_exit_strategy_testing",
    "./covid_exit_strategy_healthcare",
    "./covid_exit_strategy_spread",
    "./covid_tracking_proj_race",
    "./covid_tracking_proj_hist",
    "./minnesota",
    "./virginia",
    ["./hhs_icu", "./hhs_icu", "./hhs_icu"],
    "./state_policy",
    "./kff",
    "./california",
]

dayofweek = date.today()
dayofweek = calendar.day_name[dayofweek.weekday()]


for i in range(len(files)):

    print(f"\n****START*****\n")

    if (files[i][1] == "minnesota") and (dayofweek != "Thursday"):
        print(f"\t> Today is not Thursday. Skipping Minnesota weekly update.")
        print(f"\n****END*****\n")
        continue
    if (files[i][1] == "covid_tracking_proj_race") and (dayofweek != "Monday" and dayofweek != "Thursday"):
        print(f"\t> Today is not Monday or Thursday. Skipping Covid Tracking Proj Race data update.")
        print(f"\n****END*****\n")
        continue
    if (files[i][1] == "COVID19StatePolicy") and (dayofweek != "Tuesday" and dayofweek != "Friday"):
        print(f"\t> Today is not Tuesday or Friday. Skipping State Policy data update.")
        print(f"\n****END*****\n")
        continue
    if (files[i][1] == "california") and (dayofweek != "Wednesday"):
        print(f"\t> Today is not Wednesday. Skipping California weekly update.")
        print(f"\n****END*****\n")
        continue

    verify = False
    counter = 1
    while verify is False:
        print(f"~~ Attempt {counter}: {files[i][1]} ~~\n")
        counter = counter + 1
        file = FileFetch(params_file=files[i])
        df = file.fetch()
        if isinstance(df, list):
            j = 0
            fns = fnames[i]
            fps = fpaths[i]
            for table in df:
                verify = file.save(table, fname=fns[j], fpath=fps[j])
                j += 1
            verify = True
        else:
            verify = file.save(df, fname=fnames[i], fpath=fpaths[i])
            if (counter == 6) and (verify == False):
                print("\tAdditional attempts also failed.  Giving up.\n")
                verify = True
    print(f"\n****END*****\n")

print("Running additional processing scripts now...\n")
vdh.clean_vdh("./virginia/*.csv")
covidactnow.clean() # preprocessor - must come before call to cdph.get_counties
cdph.get_counties()
