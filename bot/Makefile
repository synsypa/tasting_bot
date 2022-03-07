APP_NAME = somm
VERSION ?= latest
ECR_REPO = 068485393558.dkr.ecr.us-west-2.amazonaws.com/${APP_NAME}:${VERSION}

ecr-login:
	aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 068485393558.dkr.ecr.us-west-2.amazonaws.com

build: 
	docker build -t ${APP_NAME}:${VERSION} .
	docker tag ${APP_NAME}:${VERSION} ${ECR_REPO}

pull: ecr-login
	docker pull ${ECR_REPO}

push: ecr-login build
	docker push ${ECR_REPO}
