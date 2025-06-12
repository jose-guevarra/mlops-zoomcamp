

build_image:
	cd src && \
	docker build -t ride-duration-prediction-service:v1 .


run:
	cd src && \
	docker run -it --rm -p 9696:9696  ride-duration-prediction-service:v1