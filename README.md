# pyhrtc
pyhrtc is a Python module to inspect various types of stable matching problems. In particular, it can handle the Hospital-Residents problem with both Ties and Couples, also known as HRTC. Having no couples reduces this to the Hospital-Residents problem with Ties, HRT, and by letting all hospitals have capacity 1 we get the Stable Marriage with Ties and Incomplete Lists problem, SMTI.

## Features

This package can currently
* read instance files in multiple formats,
* write instance files,
* inspect agents (residents and hospitals),
* combine some pairs of agents into couples,
* find maximum size matchings,
* find maximum size and maximum weight stable matchings.

## Status
[![Build status](https://travis-ci.org/IP-MATCH/pyhrtc.svg?branch=master)](https://travis-ci.org/IP-MATCH/pyhrtc)

## File formats

This package supports a number of file formats. For these, we will talk about
the set of "left" and "right" agents. These are the two bi-partitions of the
agents, such that agents on the left may only express preferences for agents on
the right, and vice-versa.

### The Glasgow format
This format used by researchers working at the University of Glasgow, or their collaborators.

The first line should just be a zero (0). The next two lines contain the number
of agents in the left and right partitions respectively. Following this, we
have one line for each agent on the left, and then one line for each agent on
the right. These are as follows:

For agents on the left, first the line contains an identifier (numeric only),
and then the preferences. Preferences within brackets indicate a tie.

For agents on the right, first the line contains an identifier (numeric only),
and then the agent's capacity, and then the preferences. Preferences within
brackets indicate a tie.

### SMTI-GRP

A CSV file containing a row-column matrix, with the first row and columns used
as identifiers, can be read in to create an instance of SMTI-GRP.

There is also a second format for SMTI-GRP, which does not have headings. This
file contains, as its first two lines, the number of rows and columns
respectively. The rest of the file is the matrix of scores, separated by spaces
only.

## Future plans

This mostly started as a tool to inspect instances of HRTC for various parameters, but it is growing. One day I might even write up a model that would solve HRTC, but that day is not today.

## Can I help?

Yes! If you want to add features, or request features, please just raise an issue. I can't promise anything, but it's good to know what people want.


