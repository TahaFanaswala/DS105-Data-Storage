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


# Used for helping format matplotlib plots
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


# Reads the College Scorecard datasets across all years for the attributes in keyAttributes
def readCollegeScorecardDatasets(keyAttributes):
    if not isinstance(keyAttributes, list):
        keyAttributes = [keyAttributes]

    # Ensures the state abbreviation and institution number is recorded in final result
    keyAttributes.append("STABBR")
    keyAttributes.append("INSTNM")

    # Used to initially store the data
    overall = {}
    # Adds the key attributes as keys in the dictionary
    for attr in keyAttributes:
        overall[attr] = []
    # Column that records the year of the datapoint
    overall["Year"] = []

    # Filepath that points to College Scorecard data from 1996 to 2013
    folder = r"D:\0_Work\Python Projects\DS105-Data-Storage\College Scorecard Datasets\datasets"
    # Iterate over each dataset and add the data to the overall dictionary
    year = 1996
    for file in os.listdir(folder):
        # Read in the dataset for the year
        path = folder + "\\" + file
        data = pd.read_csv(path)

        # Iterate over each attribute
        for key in keyAttributes:
            # Add all the data for that attribute to the dictionary
            overall[key] += list(data[key])

        # Record the year that the data was collected
        for i in range(data.shape[0]):
            overall["Year"].append(year)

        # Increment year to move to next dataset
        year += 1

    # Transform the dictionary into a dataframe
    overall = pd.DataFrame.from_dict(overall)
    # Exclude all data from US territories
    overall = overall[overall["STABBR"].isin(states)]

    # Since the key attributes list was modified at the beginning, we undo the changes
    keyAttributes.remove("STABBR")
    keyAttributes.remove("INSTNM")

    # return the final dataframe
    return overall


# Determines how many institutions are in a state in a given year
def getSchoolCounts(year):
    # Read in college scorecard data. The attribute doesn't matter since we are only interested in the
    # gathering the counts of each state in a particular year
    data = readCollegeScorecardDatasets(["PBI"])
    # Exclude data that is not from the year in question
    data = data[data["Year"] == year]
    # Count how many times each state abbrevation shows up in the filtered data, and store the results in
    # a dictionary. Keys are the state abbrevation and value is the count
    counts = Counter(data["STABBR"])
    # Sort the state abbreviations by the count in descending order
    counts = dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))

    # Return the dictionary
    return counts


# Creates a time series graph of a particular attribute
def plotAttributeTimeSeries(attr, name):
    # Read in the data across time for the attribute in question
    data = readCollegeScorecardDatasets([attr])

    # Gather all years
    years = pd.unique(data["Year"])

    # Initialize dataframe that stores results
    filtered = pd.DataFrame()

    # Iterate over each year
    for i in range(len(years)):
        # Get the year and store it into the filtered dataframe
        year = years[i]
        filtered.at[i, "Year"] = year
        # Iterate over each state
        for state in states:
            # Gather the attribute's values for that state in the year of interest
            sub = data[(data["Year"] == year) & (data["STABBR"] == state)][attr]
            # Drop null values
            sub.dropna(inplace=True)

            # Calculate the average
            avg = np.average(sub)

            # Store the result in the dataframe, and assign it to the proper state
            filtered.at[i, state] = avg

    # Get the top 10 states in terms of number of institutions in 2013
    schools = list(getSchoolCounts(2013).keys())[:11]
    schools.append("Year")

    filtered = filtered[schools]

    # Format and show the plot
    sns.set(rc={"figure.figsize": (11.7, 8.27)})

    setup = pd.melt(filtered, "Year", value_name=name)
    ax = sns.lineplot(x="Year", y=name, hue="variable", data=setup)
    sns.move_legend(ax, loc="upper left", title="State", bbox_to_anchor=(1, 1))
    ax.set_title(name + " over time")

    plt.show()


# Generates a bar chart for a particular attribute in a given year by aggregating the data to a
# state level
def barChartCollegeScorecardData(attr, name, year):
    # Read the College Scorecard Data and exclude any data not from the year in question
    data = readCollegeScorecardDatasets(attr)
    data = data[data["Year"] == year]

    # Initialize transformed dataframe
    averages = pd.DataFrame()
    # Iterate over each state
    for i in range(len(states)):
        # Get the state abbreviation
        state = states[i]

        # Gather the datapoints for that state and drop null values
        sub = data[data["STABBR"] == state]
        sub.dropna(inplace=True)

        # Get the values for that attribute, average them, and store them in the averages dataframe
        avg = np.average(sub[attr])
        averages.at[i, "State"] = state
        averages.at[i, name] = avg

    # Generate the bar chart and show it
    sns.barplot(x="State", y=name, data=averages).set_title(f"{name} in {year} by State")
    plt.show()


# Aggregates the institutional data on a state level
def transformAttrsToStateLevel(attrs, name, year, save=True):
    if not isinstance(attrs, list):
        attrs = [attrs]
    # Read in the raw data for all years for the list of attributes in attrs
    data = readCollegeScorecardDatasets(attrs)
    # Filter the data to only include the year of interest
    data = data[data["Year"] == year]

    # Aggregated results are stored here
    saveVal = pd.DataFrame()
    # Iterate over all states to aggregate the data
    index = 0
    for state in states:
        # Focus only on institutions in the state of interest
        sub = data[data["STABBR"] == state]
        # Record the state abbreviation in the aggregated dataframe
        saveVal.at[index, "State"] = state

        # Iterate over each attribute in attrs
        for attr in attrs:
            # Gather all data points that are not null
            points = list(sub[attr].dropna())
            # Average the results
            avg = np.average(points)
            # Save the result in the aggregated dataframe
            saveVal.at[index, attr] = avg

        # Move onto the next row in the aggregated dataframe
        index += 1

    # Either save the dataframe to an excel spreadsheet, or return the dataframe
    if save:
        xlw = pd.ExcelWriter("Visualization Datasets\\" + name + ".xlsx")
        saveVal.to_excel(xlw, sheet_name="main", index=False)
        xlw.save()
    else:
        return saveVal


# Creates a plot that scatter plots median debt vs median earnings data gathered in 2011
# and segregates the data point based on which quartile of the share of black undergraduates
# each institution belongs in.
def boxPlotBlackInst():
    # Gathers data on share of black undergraduate students, median debt, and median earnings after graduation
    data = readCollegeScorecardDatasets(["UGDS_BLACK", "DEBT_MDN", "mn_earn_wne_p6"])
    # Filteres the data to only focus on 2011
    data = data[data["Year"] == 2011]
    # Removes any rows where the value is privacy suppressed
    data.replace("PrivacySuppressed", None, inplace=True)
    data.dropna(inplace=True)
    data.reset_index(inplace=True, drop=True)

    # Creates a box plot based on the institutional data on black undergraduate share
    sns.boxplot(data=data, x="UGDS_BLACK")
    plt.show()

    # Gathers the actual quartile ranges
    desc = data["UGDS_BLACK"].describe()
    quartiles = [desc["25%"], desc["50%"], desc["75%"]]
    # Assigns each university a quartile rank based on the thresholds above.
    # 1 means the institution ranks in the bottom 25% in terms of black undergraduate share
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

    # Transforms the median debt and median earnings data into floating points
    data[["DEBT_MDN", "mn_earn_wne_p6"]] = data[["DEBT_MDN", "mn_earn_wne_p6"]].astype(float)

    # Creates the plot of data, where the institutions are separated based on their quartile rankings
    sns.relplot(data=data, x="DEBT_MDN", y="mn_earn_wne_p6", col="Quartile")
    plt.show()


# Counts how many null values there are for both single year attributes and multiyear attributes
def generateNullCountTables():
    # CDR3 data uses the data gathered in year 2013, although it refers to the 2011 fiscal year CDR cohort
    # Null values for TUITIONFEE_IN and TUITIONFEE_OUT are collected over time
    # C150_4_* comes from the data gathered in year 2013
    # Null values for UGDS_* are collected over time
    oneYearOnly = ["CDR3",
                   "C150_4_WHITE", "C150_4_BLACK", "C150_4_HISP", "C150_4_ASIAN", "C150_4_NHPI",
                   "C150_4_NRA", "C150_4_UNKN"]
    YEAR = 2013

    multiYear = ["TUITIONFEE_IN", "TUITIONFEE_OUT", "UGDS_WHITE", "UGDS_BLACK", "UGDS_HISP", "UGDS_ASIAN"]

    # Read in the data for the single year attributes, and filter the data to only focus on that year
    data = readCollegeScorecardDatasets(oneYearOnly[:])
    data = data[data["Year"] == YEAR]

    # Initialize the dataframe that will be saved
    saveVal = pd.DataFrame()

    # Iterate over each state
    for state in states:
        # Iterate over each single year attribute
        for attr in oneYearOnly:
            # Gather the data points for the state and attribute in question
            sub = data[data["STABBR"] == state][attr]

            # Count how many nulls there are and save the result in the dataframe
            nullCount = sub.isna().sum()
            saveVal.at[state, attr] = nullCount

    # Save the results to the excel spreadsheet for single year attributes
    saveVal.to_excel("Visualization Datasets\\One Year Attributes Null Counts.xlsx")

    # Read in the data for multiyear attributes
    data = readCollegeScorecardDatasets(multiYear[:])

    # Iterate over each attribute
    for attr in multiYear:
        # Initialize the save dataframe
        saveVal = pd.DataFrame()

        # Iterate over each year
        for year in data["Year"].unique():
            # Gather the data that is part of the year in question
            sub = data[data["Year"] == year]

            # Iterate over each state
            for state in states:
                # Gather the datapoints for the state in question for the attribute
                stateVals = sub[sub["STABBR"] == state][attr]

                # Count how many nulls there are and save them in the dataframe
                nullCount = stateVals.isna().sum()
                saveVal.at[state, year] = nullCount

        # Save the dataframe to an excel spreadsheet
        saveVal.to_excel(f"Visualization Datasets\\{attr} Null Counts Over Time.xlsx")


# Counts the number of institutions over time
def countInstOverTime():
    # Initialize save dataframe
    saveVal = pd.DataFrame()
    # Generate list of years from 1996 to 2013
    years = range(1996, 2014)

    # Create a column of states, and set it as the index
    saveVal["State"] = states
    saveVal.set_index("State", inplace=True)

    # Iterate over each year
    for year in years:
        # Get the counts of schools for each state in the given year
        counts = getSchoolCounts(year)
        # Store the results in the save dataframe
        for state in states:
            saveVal.at[state, year] = counts[state]

    # Save the results to an excel spreadsheet
    saveVal.to_excel("Visualization Datasets\\instiution count data.xlsx")


# Calculates what percent of values are null for each state and year based on the number of institutions
# in that state.
def percentAdjustNullCounts():
    # Read in the institution count and one year null count data
    instCountOverTime = pd.read_excel("Visualization Datasets\\instiution count data.xlsx",
                                      sheet_name="Sheet1").set_index("Unnamed: 0")
    oneYearNullCounts = pd.read_excel("Visualization Datasets\\One Year Attributes Null Counts.xlsx",
                                      sheet_name="Sheet1").set_index("Unnamed: 0")

    # Initialize list of one year attributes and store the year they're from
    oneYearOnly = ["CDR3",
                   "C150_4_WHITE", "C150_4_BLACK", "C150_4_HISP", "C150_4_ASIAN", "C150_4_NHPI",
                   "C150_4_NRA", "C150_4_UNKN"]
    YEAR = 2013

    # Initialize the save value for the single year attributes
    saveVal = pd.DataFrame()
    # Iterate over each state
    for state in states:
        # Gather the count of institutions in that state and year
        instCount = instCountOverTime.at[state, YEAR]
        # Iterate over each attribute
        for attr in oneYearOnly:
            # Get the count of nulls for that state and attribute
            nulls = oneYearNullCounts.at[state, attr]

            # Calculate the percent null using the institution count
            percent = nulls / instCount

            # Store the result in the save value
            saveVal.at[state, attr] = percent
    # Store the results in another sheet in the original one-year attributes spreadsheet
    xlw = pd.ExcelWriter("Visualization Datasets/One Year Attributes Null Counts.xlsx",
                         engine="openpyxl", mode="a", if_sheet_exists="replace")
    saveVal.to_excel(xlw, sheet_name="Percent")
    xlw.save()
    xlw.close()

    # Initialize list of multiyear attributes
    multiYear = ["TUITIONFEE_IN", "TUITIONFEE_OUT", "UGDS_WHITE",
                 "UGDS_BLACK", "UGDS_HISP", "UGDS_ASIAN"]

    # Iterate over each attribute
    for attr in multiYear:
        # Read in null count data for that attribute
        path = f"Visualization Datasets\\{attr} Null Counts Over Time.xlsx"
        data = pd.read_excel(path, sheet_name="Sheet1").set_index("Unnamed: 0")

        # Initialize save dataframe
        saveVal = pd.DataFrame()

        # Iterate over each state
        for state in states:
            # Iterate over each year
            for col in data.columns:
                # Get institution count for that state and year
                instCount = instCountOverTime.at[state, col]
                # Get number of nulls for that state and year
                nulls = data.at[state, col]

                # Calculate percent of null values and store in save value
                percent = nulls / instCount
                saveVal.at[state, col] = percent

        # Store the results in a new sheet called "Percent" in the relevant excel spreadsheet for that attribute
        xlw = pd.ExcelWriter(path, engine="openpyxl", mode="a", if_sheet_exists="replace")
        saveVal.to_excel(xlw, sheet_name="Percent")
        xlw.save()
        xlw.close()


# Generates a stacked bar chart for the null percent for single year attributes
# aggregated across all data for the year of 2013
def generateStackedBarChartOneYearAttributesNullCount():
    # Read in institution count and null counts
    instCountOverTime = pd.read_excel("Visualization Datasets/instiution count data.xlsx",
                                      sheet_name="Sheet1").set_index("Unnamed: 0")
    oneYearAttrNullCounts = pd.read_excel("Visualization Datasets/One Year Attributes Null Counts.xlsx",
                                          sheet_name="Sheet1").set_index("Unnamed: 0")

    # Initialize list of single year attributes and the year they're from
    oneYearOnly = ["CDR3",
                   "C150_4_WHITE", "C150_4_BLACK", "C150_4_HISP", "C150_4_ASIAN", "C150_4_NHPI",
                   "C150_4_NRA", "C150_4_UNKN"]
    YEAR = 2013

    # Initialize transformed dataframe
    transformedData = pd.DataFrame()

    # Count how many institutions were in the US across the 50 states and DC in 2013
    totalInst = sum(instCountOverTime[YEAR])
    # Iterate over each attribute
    for attr in oneYearOnly:
        # Count how many nulls are present in total across all 50 states and DC
        sumNulls = sum(oneYearAttrNullCounts[attr])

        # Store the results in the transformed dataframe
        transformedData.at[attr, "Null"] = sumNulls / totalInst
        # Used to create contrasting bar for not null percent
        transformedData.at[attr, "Not Null"] = 1

    # Set the index to be the attribute
    transformedData.reset_index(inplace=True)
    transformedData.rename(columns={"index": "Attribute"}, inplace=True)

    # Formats the resulting plot
    matplotlib.rc("axes", labelsize=20)
    matplotlib.rc("font", size=15)

    # Creates the two bars
    bar1 = sns.barplot(x="Attribute", y="Not Null", data=transformedData, color="blue").set_title(
        "Percent of entries with null value")
    bar2 = sns.barplot(x="Attribute", y="Null", data=transformedData, color="red")

    # Provides additional formatting for the plot
    topBar = mpatches.Patch(color="blue", label="Not Null")
    bottomBar = mpatches.Patch(color="red", label="Null")
    plt.legend(handles=[topBar, bottomBar])
    plt.ylabel("Percent")

    # Shows the plot
    plt.show()


# Plots the null percent over time for multi-year attributes
def timeSeriesNullPercentageForMultiYearAttributes():
    # Read in the institution count data
    instCountOverTime = pd.read_excel("Visualization Datasets/instiution count data.xlsx",
                                      sheet_name="Sheet1").set_index("Unnamed: 0")

    # Initialize list of multi-year attributes
    multiYear = ["TUITIONFEE_IN", "TUITIONFEE_OUT", "UGDS_WHITE", "UGDS_BLACK", "UGDS_HISP", "UGDS_ASIAN"]

    # Initialize transformed dataframe
    transformedData = pd.DataFrame()
    index = 0

    # Iterate over each attribute
    for attr in multiYear:
        # Open the null count spreadsheet for the attribute in question
        path = f"Visualization Datasets\\{attr} Null Counts Over Time.xlsx"
        data = pd.read_excel(path, sheet_name="Sheet1").set_index("Unnamed: 0")
        # Iterate over each year
        for year in instCountOverTime.columns:
            # Count how many institutions were in the 50 states and DC in the year in question
            # and how many null counts were there for the attribute in question in that year
            sumInst = sum(instCountOverTime[year])
            totalNulls = sum(data[year])

            # Store the attribute, year, and null percent in the transformed dataframe
            transformedData.at[index, "Attribute"] = attr
            transformedData.at[index, "Year"] = int(year)
            transformedData.at[index, "Null Percent"] = totalNulls / sumInst

            # Increment the row to move to next year
            index += 1

    # Format the plot
    matplotlib.rc("axes", labelsize=20)
    matplotlib.rc("font", size=15)

    # Generate the plot
    sns.lineplot(data=transformedData, x="Year", y="Null Percent", hue="Attribute").set_title(
        "Percent of entries with null value over time")

    # Format the x ticks
    plt.xticks(computeTicks(transformedData["Year"], step=1))

    # Show the plot
    plt.show()


# Generate a correlation matrix using values from the year 2013 for both single and multiyear attributes
# Makes two correlation matrices: 1 where data is aggregated on state level, and one where data remains at
# institutional level
def generateCorrelationMatrix():
    # Initialize lists of multi and single year attributes
    multiYear = ["TUITIONFEE_IN", "TUITIONFEE_OUT", "UGDS_WHITE", "UGDS_BLACK", "UGDS_HISP", "UGDS_ASIAN"]
    oneYearOnly = ["CDR3",
                   "C150_4_WHITE", "C150_4_BLACK", "C150_4_HISP", "C150_4_ASIAN", "C150_4_NHPI",
                   "C150_4_NRA", "C150_4_UNKN"]

    # Generate combined list
    attrs = multiYear + oneYearOnly

    # Aggregate the data into state level
    data = transformAttrsToStateLevel(attrs, "", 2013, False)

    # Generate a correlation matrix from the state data
    corrMatrix = data.corr()

    # Format and show the plot
    f, ax = plt.subplots(figsize=(20, 20))

    g = sns.heatmap(corrMatrix, ax=ax, annot=True)
    g.set_xticklabels(g.get_xmajorticklabels(), fontsize=8)
    g.set_yticklabels(g.get_ymajorticklabels(), fontsize=8)
    plt.show()

    # Read in the raw data for all attributes
    baseData = readCollegeScorecardDatasets(attrs)
    # Exclude all data not from 2013
    baseData = baseData[baseData["Year"] == 2013]
    # Drop any institutions that don't have values for all attributes in question
    baseData.dropna(inplace=True)
    baseData.drop(["Year"], inplace=True, axis=1)

    # Generate correlation matrix
    baseCorr = baseData.corr()

    # Format and show the plot
    f, ax = plt.subplots(figsize=(20, 20))
    g = sns.heatmap(baseCorr, ax=ax, annot=True)
    g.set_xticklabels(g.get_xmajorticklabels(), fontsize=8)
    g.set_yticklabels(g.get_ymajorticklabels(), fontsize=8)
    plt.show()


# Generates geo plot given excel spreadsheet data, sheetname, attribute, and name
def generateGeoPlot(sourceData, attr, sheetname, title):
    # Reads in a shape file used to structure the geoplot
    statesDF = gpd.read_file("tl_2017_us_state/tl_2017_us_state.shp")
    # Ensures that we only focus on 50 states and DC
    statesDF = statesDF[statesDF["STUSPS"].isin(states)]

    # Reads in the data in the spreadsheet
    data = pd.read_excel(sourceData, sheet_name=sheetname)

    # Generates the chloropleth map
    fig = px.choropleth(data, locations="State", geojson=statesDF, color=attr,
                        scope="usa", locationmode="USA-states", title=title,
                        color_continuous_scale="rdbu_r")
    # Shows the plot. Unlike matplotlib, the maps are generated in browser
    fig.show()


# Creates a plot that charts the percent of students in debt each year on a bar chart, and the total enrollment
# of students on a line chart
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


# Creates a scatter plot which shows the relationship between four year completion percentage and default rate
def createRaceVCompletionScatterPlots():
    root = "C150_4_"
    attrs = ["WHITE", "BLACK", "ASIAN"]

    # Creates list of attributes for four year completion percentage for white, asian, and black students
    names = []
    for race in attrs:
        names.append(root + race)

    # Read in the completion data and default rate data and exclude any data not from 2013
    # Also drop institutions that contain any null values for any of the attributes in question
    data = readCollegeScorecardDatasets(names + ["CDR3"])
    data = data[data["Year"] == 2013].dropna()

    # Iterate over each race and generate the scatter plot
    for race in attrs:
        ax = sns.regplot(data=data, x=root + race, y="CDR3", line_kws={"color": "red"}, marker="+")
        ax.set_xlabel(f"4 year completion percentage: {race.lower()} students")
        ax.set_ylabel("Default Rate")
        plt.show()


# Generates a histogram for an attribute's values in a given year
def histogramGenerator(attr, year):
    # Read in the attribute's data and exclude any data not from the given year
    data = readCollegeScorecardDatasets([attr])
    data = data[data["Year"] == year]

    # Generate the histogram. By default, seaborn excludes any null values
    # Also generates a kde line, which also shows the distribution data
    ax = sns.histplot(data=data, x=attr, kde=True, stat="count", bins=25)
    ax.lines[0].set_color("crimson")
    ax.set_xlabel("Default Rate")
    ax.set_title("Histogram of default rates across universities")
    plt.show()
