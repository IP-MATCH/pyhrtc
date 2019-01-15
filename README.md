# pyhrtc
pyhrtc is a Python module to inspect various types of stable matching problems. In particular, it can handle the Hospital-Residents problem with both Ties and Couples, also known as HRTC. Having no couples reduces this to the Hospital-Residents problem with Ties, HRT, and by letting all hospitals have capacity 1 we get the Stable Marriage with Ties and Incomplete Lists problem, SMTI.

## Features

This package can currently
* read instance files in multiple formats,
* write instance files,
* inspect residents and hospitals,
* combine some pairs of doctors into couples, and
* find maximum size matchings (not necessarily stable).

## Status
![Build status](https://travis-ci.org/IP-MATCH/pyhrtc.svg?branch=master)

## File formats

Currently this package only really supports what is colloquially known as the Glasgow file format, the format used by researchers working at the University of Glasgow, or their collaborators.

## Future plans

This mostly started as a tool to inspect instances of HRTC for various parameters, but it is growing. One day I might even write up a model that would solve HRTC, but that day is not today.

## Can I help?

Yes! If you want to add features, or request features, please just raise an issue. I can't promise anything, but it's good to know what people want.


