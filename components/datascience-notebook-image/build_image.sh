#!/usr/bin/env bash
#
# A simple script to build the Docker images.
# This is intended to be invoked as a step in Argo to build the docker image.
#
# build_image.sh ${DOCKERFILE} ${IMAGE} ${TAG}
set -ex

DOCKERFILE=$1
CONTEXT_DIR=$(dirname "$DOCKERFILE")
IMAGE=$2
# The tag for the image
TAG=$3
# Takes a value of true or false. Determines if we should tag the image
# with the "latest" tag
#
# TODO(jlewi): We should take in the json config file and then parse that.
CONFIG_FILE=$4
BASE_IMAGE=$(jq -r .BASE_IMAGE ${CONFIG_FILE})

# JQ returns null for non defined values.
if [ ${BASE_IMAGE} == "null" ]; then
  BASE_IMAGE=""
fi

# Wait for the Docker daemon to be available.
until docker ps; do
  sleep 3
done

docker build --pull \
  --build-arg "BASE_IMAGE=${BASE_IMAGE}" \
  -t "${IMAGE}:${TAG}" \
  -f ${DOCKERFILE} ${CONTEXT_DIR}

gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
gcloud docker -- push "${IMAGE}:${TAG}"
if [[ "${IS_LATEST}" == "true" ]]; then
  docker tag "${IMAGE}:${TAG}" "${IMAGE}:latest"
  gcloud docker -- push "${IMAGE}:latest"
fi
