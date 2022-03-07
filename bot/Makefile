APP_NAME = somm
VERSION ?= latest
ECR_REPO = public.ecr.aws/b3k6x0d7
CONTAINER = ${ECR_REPO}/${APP_NAME}:${VERSION}

ecr-login:
	aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin ${ECR_REPO}

build: 
	docker build -t ${APP_NAME}:${VERSION} .
	docker tag ${APP_NAME}:${VERSION} ${CONTAINER}

pull: ecr-login
	docker pull ${CONTAINER}

push: ecr-login build
	docker push ${CONTAINER}
