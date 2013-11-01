# About

Uploads a raster images (GeoTIFFs) to Google Maps Engine.

# Usage

Command line:

    mapsengineupload.py --email=1011838452455@developer.gserviceaccount.com --key=~/Projects/skytruth/mapserver/key.p12 --projectid=06136759344167181854 --attribution="Copyright SKYTRUTH" --tags="testegil,testother" ~/Downloads/Test/*/*.tiff

The directory contains the following matching files:

    /home/redhog/Downloads/Test/Blubb/2008Tioga_0_35000.tiff
    /home/redhog/Downloads/Test/Blah/2008Tioga_0_10000.tiff
    /home/redhog/Downloads/Test/Blah/2008Tioga_10000_0.tiff

And the following auxillary files:

    /home/redhog/Downloads/Test/Blubb/__directory__.info
    /home/redhog/Downloads/Test/Blah/__directory__.info
    /home/redhog/Downloads/Test/Blah/2008Tioga_0_10000.info

Example content for one such info file:

    {"tags": ["Blubbetiblubb and more stuff", "Even more stuff"]}

# Installation

    git clone git@github.com:SkyTruth/gme_tools.git
    cd gme_tools
    virtualenv deps
    source deps/bin/activate
    python setup.py install

# How to go Google Maps Engine key

    Server to Server Authentication (service accounts)- allows your server to edit google maps engine
    https://developers.google.com/maps-engine/documentation/oauth/serviceaccount
