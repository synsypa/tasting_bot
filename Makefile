HUB ?= synsypa
VERSION ?= latest

IMAGE ?= markov_tasting

.PHONY: build push pull deploy

build: Dockerfile
	docker build -t $(HUB)/$(IMAGE):$(VERSION) -f Dockerfile .

push:
	docker push $(HUB)/$(IMAGE):$(VERSION)

pull:
	docker pull $(HUB)/$(IMAGE):$(VERSION)

deploy:
	docker run --restart unless-stopped -d \
	-e SOMM_TWEET_CONSUMER_KEY=$(SOMM_TWEET_CONSUMER_KEY) \
	-e SOMM_TWEET_CONSUMER_SECRET=$(SOMM_TWEET_CONSUMER_SECRET) \
	-e SOMM_TWEET_ACCESS_KEY=$(SOMM_TWEET_ACCESS_KEY) \
	-e SOMM_TWEET_ACCESS_SECRET=$(SOMM_TWEET_ACCESS_SECRET) \
	$(HUB)/$(IMAGE):$(VERSION)

test:
	echo $(SOMM_TWEET_CONSUMER_KEY)
