# Berlin United LogCrawler

## Container
The Dockerfile contains all the python packages that are needed to run all the code related to logs. The image is build by the CI and pushed to our gitlab container registry. This image will be used for all code running inside k8s.

You can start the container locally as well and run the scripts in there:
```
docker build -t logcrawler:latest .
docker run -it logcrawler:latest /bin/bash

docker run -it -v ${PWD}:/test logcrawler:latest /bin/bash
```

## Run locally
You need to make sure that you have the required system packages installed. Have a look in the Dockerfile for the needed packages for an Ubuntu based distro.

The code expects it has filesystem access to the logs folder. You can use sshfs for that.

You need to set the environment variables:
```bash
export LOG_ROOT=
export DB_PASS=
export MINIO_PASS=
```