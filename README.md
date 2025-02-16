# Berlin United LogCrawler
Collection of scripts for parsing our logs and adding the data to our postgres database. This is primarily intended to be used with our Visual Analytics Tool https://github.com/efcy/visual_analytics.


## Container
The Dockerfile contains all the python packages that are needed to run all the code related to logs. The image is build by the CI and pushed to our gitlab container registry. This image will be used for all code running inside k8s.

You can start the container locally as well and run the scripts in there:
```
docker build -t logcrawler:latest .
docker run -it logcrawler:latest /bin/bash

docker run -it -v ${PWD}:/test logcrawler:latest /bin/bash
```
