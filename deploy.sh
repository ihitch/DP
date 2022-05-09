#!/bin/bash
if [[ $# != 1 ]]; then
	echo "usage: $0 <image_name>"
	exit -1
fi


IMAGE_NAME="$1"

set -ex

# remove data files
rm -rf _trace _workflows .nextflow* db.json 

# build docker image
docker build -t ${IMAGE_NAME} .
docker push ${IMAGE_NAME}


minikube start
minikube addons enable metrics-server

# deploy helm chart to kubernetes cluster 
helm uninstall nextflow-api
helm install nextflow-api ./helm

kubectl create rolebinding default-edit --clusterrole=edit --serviceaccount=default:default
kubectl create rolebinding default-view --clusterrole=view --serviceaccount=default:default

minikube dashboard
minikube service nextflow-api --url 