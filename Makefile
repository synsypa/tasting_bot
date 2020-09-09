HUB ?= synsypa
VERSION ?= latest

IMAGE ?= markov_tasting

.PHONY: build push pull

build: Dockerfile
	docker build -t $(HUB)/$(IMAGE):$(VERSION) -f Dockerfile .

push:
	docker push $(HUB)/$(IMAGE):$(VERSION)

pull:
	docker pull $(HUB)/$(IMAGE):$(VERSION)