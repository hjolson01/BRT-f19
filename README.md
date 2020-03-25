# WISC-BRT-Fall2019
Stats on proposed BRT routing plan

Redundant Bus Routes in the City of Madison: 

With the new BRT transportation system months away from breaking ground, we set out to find any inefficiencies that this rapid transportation system would cause to the existing bus traffic network. This repository contains Jupyter notebooks, a python file, as well as various public data samples in order to log current progress.

Methodology
Establishing a solid visual context was the first concern, using Geopandas and Pandas DataFrames. The data contained geographic measures so route overlays were possible within a single plot.

Preprocessing involved categorization of certain existing bus stops within walking distance to a proposed BRT stop location. Since the new transportation network is centered around rapid transportation, the difference in timing involved with each route arrival and departure was minimal. We classified walking distance as within a half kilometer, or about a 5-minute walk.

Results
On average, about 17% of the total existing bus stops were redundant. However, a closer look at the findings reveals that those inefficient bus stops had about 16% higher ridership, located in most high-density areas of the city. Certain routes also had much higher proportions of inefficient stops than others.

Of these routes, we recommend elimination of routes 1, 4, 5, 27, 28, 44, 48, and 67 because these routes alone would cost in excess of $132,000 annually to maintain based off of budget estimates of $2,500 per stop.

Authors

John Kitaoka

Hunter Olson 

Jin Woo Lee 
