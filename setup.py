from os import path
from setuptools import setup


DISTNAME = "earthpy"
DESCRIPTION = "A set of helper functions to make working with spatial data in open source tools easier. This package is maintained by Earth Lab and was originally designed to support the earth analytics education program."
MAINTAINER = "Leah Wasser"
MAINTAINER_EMAIL = "leah.wasser@colorado.edu"


# read the contents of your README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()


if __name__ == "__main__":
    setup(
        name=DISTNAME,
        maintainer=MAINTAINER,
        maintainer_email=MAINTAINER_EMAIL,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type="text/markdown",
        version="0.6.4",
        packages=["earthpy"],
        install_requires=[
            "download",
            "geopandas",
            "matplotlib>=2.0.0",
            "numpy>=1.14.0",
            "rasterio",
            "Rtree>=0.8",
            "scikit-image",
        ],
        zip_safe=False,  # the package can run out of an .egg file
        classifiers=[
            "Intended Audience :: Developers",
            "License :: OSI Approved :: BSD License",
            "Programming Language :: Python",
            "Topic :: Software Development",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: POSIX",
            "Operating System :: Unix",
            "Operating System :: MacOS",
        ],
        package_data={
            DISTNAME: [
                "example-data/*.json",
                "example-data/*.tif",
                "example-data/*.geojson",
                "example-data/*.shp",
                "example-data/*.shx",
                "example-data/*.prj",
                "example-data/*.dbf",
            ]
        },
    )
