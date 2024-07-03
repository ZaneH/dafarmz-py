mongodb:
	# MONGO_URL=mongodb://mongoadmin:secret@localhost:27017
	docker run -d --name dafarmz-mongo \
        -e MONGO_INITDB_ROOT_USERNAME=mongoadmin \
        -e MONGO_INITDB_ROOT_PASSWORD=secret \
        -p 27017:27017 mongo