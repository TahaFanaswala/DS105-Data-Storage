# Understanding The Impacts Race Has On Student Loan Repayment 

## Data cleaning for analysis: 

The Obama administration aimed to increase the transparency of the higher education system by releasing vast pools of data through the college scorecard. The scorecard provides data which is sufficient for us to be able to measure discrepancies influencing higher education through gender, race, and social class. Our project looks to utilise this availability of big data to understand the impacts that race has on the various educational outcomes of university students, specifically looking at how student loans discriminate against various races. 

The nature of the college scorecard dataset that we are using is not in the rawest form since it has been aggregated at the school level, however, the astounding volume of null and missing values meant that the dataset was very tedious to work with. The contents of this dataset include 1805 variables for 7149 universities across the United States which spans from 1996 to 2015. When initially exploring the raw data, we found there to be a large volume of missing values and inconsistencies in the attributes which were recorded over the years as many were discontinued. All these variations within the data frame have the potential to skew the data. In order to prevent biases in our base data that lead to invalid results, we look to conduct basic visualizations of the shape of our data.

### Percentage null values for various attributes: observing the gaps in the data 

*
We have initially visualised the shape and the contents of our data by showcasing the proportion of missing values with seaborn displot. We had prior narrowed down the attributes which related to race and the various factors we wished to compare. This displot shows how the various attributes are hereby concentrated with null values especially C150_4_NHPI which showcases an above 90% of values within the attribute are null.

### Percentage of null values for each attribute analysed: time series 

