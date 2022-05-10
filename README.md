# DP

This repository includes the source code of the master's thesis project.


## Requirements
- git
- docker
- minikube
- kubectl
- helm

## Installation
1) `git clone`
2) `cd DP`
3) In DP/helm/values.yaml edit image to the name you want or leave it as it is
	```
	WebServer:
		Image:
	```
4) In case you changed image name use 
	```
	./deploy.sh <image_name>
	```
	Otherwise 
	```
	./deploy.sh
	```