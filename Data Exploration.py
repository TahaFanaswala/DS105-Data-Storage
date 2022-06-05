import os
import matplotlib
import pandas as pd
import numpy as np
import math
import warnings
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib
from matplotlib.ticker import PercentFormatter
from collections import Counter
import plotly.express as px
import geopandas as gpd

warnings.simplefilter("ignore")

states = ['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA',
          'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME',
          'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM',
          'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX',
          'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']


def computeTicks(x, step=5):
    """
    Computes domain with given step encompassing series x
    @ params
    x    - Required - A list-like object of integers or floats
    step - Optional - Tick frequency
    """
    xMax, xMin = math.ceil(max(x)), math.floor(min(x))
    dMax, dMin = xMax + abs((xMax % step) - step) + (step if (xMax % step != 0) else 0), xMin - abs((xMin % step))
    return range(dMin, dMax, step)


def readFREDdata():
    file = r"D:\0_Work\Pycharm\DS105-Data-Storage\FRED Data\FGCCSAQ027S.xls"

    data = pd.read_excel(file, sheet_name="FRED Graph")

    stop = False
    index = 0

    while not stop:
        value = data.at[index, data.columns[0]]

        if value != "observation_date":
            data.drop(labels=[index], inplace=True)
            index += 1
        else:
            data.drop(labels=[index], inplace=True)
            stop = True

    data.reset_index(drop=True, inplace=True)
    data.rename(mapper={data.columns[0]: "Observation", data.columns[1]: "Student Loans in Millions"},
                inplace=True, axis=1)

    print(data.head())


def readKaggleDatasets(keyAttributes):
    keyAttributes.append("STABBR")
    keyAttributes.append("INSTNM")
    overall = {}
    for attr in keyAttributes:
        overall[attr] = []

    overall["Year"] = []

    folder = r"D:\0_Work\Python Projects\DS105-Data-Storage\Kaggle Datasets\datasets"
    year = 1996
    for file in os.listdir(folder):
        path = folder + "\\" + file

        data = pd.read_csv(path)

        for key in keyAttributes:
            overall[key] += list(data[key])

        for i in range(data.shape[0]):
            overall["Year"].append(year)

        year += 1

    overall = pd.DataFrame.from_dict(overall)
    overall = overall[overall["STABBR"].isin(states)]

    keyAttributes.remove("STABBR")
    keyAttributes.remove("INSTNM")

    return overall


def getSchoolCounts():
    data = pd.read_csv("test.csv")
    data = data[data["Year"] == 2013]
    counts = Counter(data["STABBR"])
    counts = dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))

    return list(counts.keys())


def plotAttributeTimeSeries(attr, name):
    data = pd.read_csv("test.csv")

    years = pd.unique(data["Year"])
    states = pd.unique(data["STABBR"])

    filtered = pd.DataFrame()

    for i in range(len(years)):
        year = years[i]
        filtered.at[i, "Year"] = year
        for state in states:
            sub = data[(data["Year"] == year) & (data["STABBR"] == state)][attr]
            sub.dropna(inplace=True)

            avg = np.average(sub)

            filtered.at[i, state] = avg

    schools = getSchoolCounts()[:11]
    schools.append("Year")

    filtered = filtered[schools]

    sns.set(rc={"figure.figsize": (11.7, 8.27)})

    setup = pd.melt(filtered, "Year", value_name=name)
    ax = sns.lineplot(x="Year", y=name, hue="variable", data=setup)
    sns.move_legend(ax, loc="upper left", title="State", bbox_to_anchor=(1, 1))
    ax.set_title(name + " over time")

    plt.show()


def barChartCollegeScorecardData(attr, name, year):
    data = pd.read_csv("test.csv")

    filtered = data[data["Year"] == year][["STABBR", attr]]

    averages = pd.DataFrame()
    for i in range(len(states)):
        state = states[i]

        sub = filtered[filtered["STABBR"] == state]
        sub.dropna(inplace=True)

        avg = np.average(sub[attr])
        averages.at[i, "State"] = state
        averages.at[i, name] = avg

    sns.barplot(x="State", y=name, data=averages).set_title(f"{name} in {year} by State")
    plt.show()


def transformAttrsToStateLevel(attrs, name, year, save=True):
    data = readKaggleDatasets(attrs)
    data = data[data["Year"] == year]
    saveVal = pd.DataFrame()
    index = 0

    for state in states:
        sub = data[data["STABBR"] == state]

        saveVal.at[index, "State"] = state

        for attr in attrs:
            points = list(sub[attr].dropna())
            avg = np.average(points)
            saveVal.at[index, attr] = avg

        index += 1

    if save:
        xlw = pd.ExcelWriter("Visualization Datasets\\" + name + ".xlsx")
        saveVal.to_excel(xlw, sheet_name="main", index=False)
        xlw.save()
    else:
        return saveVal


def boxPlotBlackInst():
    data = readKaggleDatasets(["UGDS_BLACK", "DEBT_MDN", "mn_earn_wne_p6"])
    data = data[data["Year"] == 2011]
    data.replace("PrivacySuppressed", None, inplace=True)
    data.dropna(inplace=True)
    data.reset_index(inplace=True, drop=True)

    sns.boxplot(data=data, x="UGDS_BLACK")
    plt.show()

    desc = data["UGDS_BLACK"].describe()

    quartiles = [desc["25%"], desc["50%"], desc["75%"]]
    for i in range(data.shape[0]):
        val = data.at[i, "UGDS_BLACK"]

        quartSet = False
        for a in range(len(quartiles)):
            bench = quartiles[a]
            if val <= bench:
                data.at[i, "Quartile"] = a + 1
                quartSet = True
                break

        if not quartSet:
            data.at[i, "Quartile"] = 4

    data[["DEBT_MDN", "mn_earn_wne_p6"]] = data[["DEBT_MDN", "mn_earn_wne_p6"]].astype(float)

    sns.relplot(data=data, x="DEBT_MDN", y="mn_earn_wne_p6", col="Quartile")
    plt.show()


def generateNullCountTables():
    # PBI isn't really used
    # CDR3 data uses the data gathered in year 2013, although it refers to the 2011 fiscal year CDR cohort
    # Null values for TUITIONFEE_IN and TUITIONFEE_OUT are collected over time
    # C150_4_* comes from the data gathered in year 2013
    # Null values for UGDS_* are collected over time
    oneYearOnly = ["CDR3",
                   "C150_4_WHITE", "C150_4_BLACK", "C150_4_HISP", "C150_4_ASIAN", "C150_4_NHPI",
                   "C150_4_NRA", "C150_4_UNKN"]
    YEAR = 2013

    multiYear = ["TUITIONFEE_IN", "TUITIONFEE_OUT", "UGDS_WHITE", "UGDS_BLACK", "UGDS_HISP", "UGDS_ASIAN"]

    data = readKaggleDatasets(oneYearOnly[:])
    data = data[data["Year"] == YEAR]

    saveVal = pd.DataFrame()

    for state in states:
        for attr in oneYearOnly:
            sub = data[data["STABBR"] == state][attr]
            nullCount = sub.isna().sum()

            saveVal.at[state, attr] = nullCount

    saveVal.to_excel("Visualization Datasets\\One Year Attributes Null Counts.xlsx")

    data = readKaggleDatasets(multiYear[:])

    for attr in multiYear:
        saveVal = pd.DataFrame()

        for year in data["Year"].unique():
            sub = data[data["Year"] == year]

            for state in states:
                stateVals = sub[sub["STABBR"] == state][attr]
                nullCount = stateVals.isna().sum()
                saveVal.at[state, year] = nullCount

        saveVal.to_excel(f"Visualization Datasets\\{attr} Null Counts Over Time.xlsx")


def countInstOverTime():
    data = readKaggleDatasets(["PBI"])

    years = list(data["Year"].unique())

    saveVal = pd.DataFrame()

    for state in states:
        for year in years:
            sub = data[(data["STABBR"] == state) & (data["Year"] == year)]
            institutions = len(sub["INSTNM"])

            saveVal.at[state, year] = institutions

    saveVal.to_excel("Visualization Datasets\\instiution count data.xlsx")


def percentAdjustNullCounts():
    instCountOverTime = pd.read_excel("Visualization Datasets\\instiution count data.xlsx",
                                      sheet_name="Sheet1").set_index("Unnamed: 0")
    oneYearNullCounts = pd.read_excel("Visualization Datasets\\One Year Attributes Null Counts.xlsx",
                                      sheet_name="Sheet1").set_index("Unnamed: 0")

    oneYearOnly = ["CDR3",
                   "C150_4_WHITE", "C150_4_BLACK", "C150_4_HISP", "C150_4_ASIAN", "C150_4_NHPI",
                   "C150_4_NRA", "C150_4_UNKN"]
    YEAR = 2013

    saveVal = pd.DataFrame()
    for state in states:
        instCount = instCountOverTime.at[state, YEAR]
        for attr in oneYearOnly:
            nulls = oneYearNullCounts.at[state, attr]

            percent = nulls / instCount

            saveVal.at[state, attr] = percent

    xlw = pd.ExcelWriter("Visualization Datasets/One Year Attributes Null Counts.xlsx",
                         engine="openpyxl", mode="a", if_sheet_exists="replace")
    saveVal.to_excel(xlw, sheet_name="Percent")
    xlw.save()
    xlw.close()

    multiYear = ["TUITIONFEE_IN", "TUITIONFEE_OUT", "UGDS_WHITE",
                 "UGDS_BLACK", "UGDS_HISP", "UGDS_ASIAN"]

    for attr in multiYear:
        path = f"Visualization Datasets\\{attr} Null Counts Over Time.xlsx"
        data = pd.read_excel(path, sheet_name="Sheet1").set_index("Unnamed: 0")

        saveVal = pd.DataFrame()

        for state in states:
            for col in data.columns:
                instCount = instCountOverTime.at[state, col]
                nulls = data.at[state, col]

                percent = nulls / instCount
                saveVal.at[state, col] = percent

        xlw = pd.ExcelWriter(path, engine="openpyxl", mode="a", if_sheet_exists="replace")
        saveVal.to_excel(xlw, sheet_name="Percent")
        xlw.save()
        xlw.close()


def generateStackedBarChartOneYearAttributesNullCount():
    instCountOverTime = pd.read_excel("Visualization Datasets/instiution count data.xlsx",
                                      sheet_name="Sheet1").set_index("Unnamed: 0")
    oneYearAttrNullCounts = pd.read_excel("Visualization Datasets/One Year Attributes Null Counts.xlsx",
                                          sheet_name="Sheet1").set_index("Unnamed: 0")

    oneYearOnly = ["CDR3",
                   "C150_4_WHITE", "C150_4_BLACK", "C150_4_HISP", "C150_4_ASIAN", "C150_4_NHPI",
                   "C150_4_NRA", "C150_4_UNKN"]
    YEAR = 2013

    transformedData = pd.DataFrame()
    totalInst = sum(instCountOverTime[YEAR])
    for attr in oneYearOnly:
        sumNulls = sum(oneYearAttrNullCounts[attr])

        transformedData.at[attr, "Null"] = sumNulls / totalInst
        transformedData.at[attr, "Not Null"] = 1

    transformedData.reset_index(inplace=True)
    transformedData.rename(columns={"index": "Attribute"}, inplace=True)

    matplotlib.rc("axes", labelsize=20)
    matplotlib.rc("font", size=15)

    bar1 = sns.barplot(x="Attribute", y="Not Null", data=transformedData, color="blue").set_title(
        "Percent of entries with null value")
    bar2 = sns.barplot(x="Attribute", y="Null", data=transformedData, color="red")

    topBar = mpatches.Patch(color="blue", label="Not Null")
    bottomBar = mpatches.Patch(color="red", label="Null")
    plt.legend(handles=[topBar, bottomBar])
    plt.ylabel("Percent")

    plt.show()


def timeSeriesNullPercentageForMultiYearAttributes():
    instCountOverTime = pd.read_excel("Visualization Datasets/instiution count data.xlsx",
                                      sheet_name="Sheet1").set_index("Unnamed: 0")

    multiYear = ["TUITIONFEE_IN", "TUITIONFEE_OUT", "UGDS_WHITE", "UGDS_BLACK", "UGDS_HISP", "UGDS_ASIAN"]

    transformedData = pd.DataFrame()
    index = 0

    saveVal = pd.DataFrame()

    for attr in multiYear:
        path = f"Visualization Datasets\\{attr} Null Counts Over Time.xlsx"
        data = pd.read_excel(path, sheet_name="Sheet1").set_index("Unnamed: 0")
        for year in instCountOverTime.columns:
            sumInst = sum(instCountOverTime[year])
            totalNulls = sum(data[year])

            transformedData.at[index, "Attribute"] = attr
            transformedData.at[index, "Year"] = year
            transformedData.at[index, "Null Percent"] = totalNulls / sumInst

            index += 1

            saveVal.at[attr, year] = totalNulls / sumInst

        saveVal.to_csv(path_or_buf="sanity check.csv")

    transformedData["Year"] = transformedData["Year"].astype(int)

    matplotlib.rc("axes", labelsize=20)
    matplotlib.rc("font", size=15)

    sns.lineplot(data=transformedData, x="Year", y="Null Percent", hue="Attribute").set_title(
        "Percent of entries with null value over time")

    plt.xticks(computeTicks(transformedData["Year"], step=1))

    plt.show()


def generateCorrelationMatrix():
    multiYear = ["TUITIONFEE_IN", "TUITIONFEE_OUT", "UGDS_WHITE", "UGDS_BLACK", "UGDS_HISP", "UGDS_ASIAN"]
    oneYearOnly = ["CDR3",
                   "C150_4_WHITE", "C150_4_BLACK", "C150_4_HISP", "C150_4_ASIAN", "C150_4_NHPI",
                   "C150_4_NRA", "C150_4_UNKN"]

    attrs = multiYear + oneYearOnly

    data = transformAttrsToStateLevel(attrs, "", 2013, False)

    corrMatrix = data.corr()

    f, ax = plt.subplots(figsize=(20, 20))

    g = sns.heatmap(corrMatrix, ax=ax, annot=True)
    g.set_xticklabels(g.get_xmajorticklabels(), fontsize=8)
    g.set_yticklabels(g.get_ymajorticklabels(), fontsize=8)
    plt.show()

    f, ax = plt.subplots(figsize=(20, 20))
    baseData = readKaggleDatasets(attrs)
    baseData = baseData[baseData["Year"] == 2013]
    baseData.dropna(inplace=True)
    baseData.drop(["Year"], inplace=True, axis=1)
    baseCorr = baseData.corr()

    g = sns.heatmap(baseCorr, ax=ax, annot=True)
    g.set_xticklabels(g.get_xmajorticklabels(), fontsize=8)
    g.set_yticklabels(g.get_ymajorticklabels(), fontsize=8)
    plt.show()


def generateGeoPlot(sourceData, attr, sheetname, title):
    statesDF = gpd.read_file("tl_2017_us_state/tl_2017_us_state.shp")
    statesDF = statesDF[statesDF["STUSPS"].isin(states)]

    data = pd.read_excel(sourceData, sheet_name=sheetname)

    fig = px.choropleth(data, locations="State", geojson=statesDF, color=attr,
                        scope="usa", locationmode="USA-states", title=title,
                        color_continuous_scale="rdbu_r")
    fig.show()


def main():
    source = "Visualization Datasets/in and out tuition fees.xlsx"
    attrs = ["TUITIONFEE_IN", "TUITIONFEE_OUT"]

    generateGeoPlot(source, attrs[0], "main", "In-state tuition by state 2013 (dollars)")
    generateGeoPlot(source, attrs[1], "main", "Out of state tuition by state 2013 (dollars)")


def createIntroVizz():
    data = pd.read_excel("Visualization Datasets/student debt percent, enrollment, and per capita debt.xlsx",
                         sheet_name="main")

    matplotlib.rc_file_defaults()
    ax1 = sns.set_style(style=None, rc=None)

    fig, ax1 = plt.subplots(figsize=(12, 6))

    sns.lineplot(data=data["Total Enrollment"], marker="o", sort=False, ax=ax1, color="red")
    ax1.set_ylabel("Total Enrollment (millions)")
    ax1.set_xlabel("Year")
    ax2 = ax1.twinx()

    sns.barplot(data=data, x="Year", y="Student Debt Percentage", alpha=0.5, ax=ax2, color="blue")
    ax2.set_ylabel("Percent of Students in Debt")

    plt.show()


def createRaceVCompletionScatterPlots():
    root = "C150_4_"
    attrs = ["WHITE", "BLACK", "ASIAN"]

    names = []
    for race in attrs:
        names.append(root + race)

    data = readKaggleDatasets(names + ["CDR3"])
    data = data[data["Year"] == 2013].dropna()

    for race in attrs:
        ax = sns.regplot(data=data, x=root + race, y="CDR3", line_kws={"color": "red"}, marker="+")
        ax.set_xlabel(f"4 year completion percentage: {race.lower()} students")
        ax.set_ylabel("Default Rate")
        plt.show()


def histogramGenerator(attr, year):
    data = readKaggleDatasets([attr])
    data = data[data["Year"] == year]

    ax = sns.histplot(data=data, x=attr, kde=True, stat="count", bins=25)
    ax.lines[0].set_color("crimson")
    ax.set_xlabel("Default Rate")
    ax.set_title("Histogram of default rates across universities")
    plt.show()


histogramGenerator("CDR3", 2013)
