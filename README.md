# Satiscribble-AI
This is the repository for Satiscribble AI. This python server is hosted with fastAPI and contains all the AI microservices needed for satiscribble.

# Setup
This github is hosted on Docker. To set up your docker image, please follow the following steps after you git clone.
```
cd build
docker compose up
```
The docker file has been setup to automatically startup the FastAPI service once the container is up.<br/>
If you update any of your code, restart the container to apply your changes to your service.<br/>

If you prefer to start the service yourself, comment out the `COMMAND` function in docker-compose.yaml and rebuild your container. <br/>
Afterwhich, enter the docker container terminal and run to start the service.

```
uvicorn main:app --port=8000 --host=0.0.0.0
```

# Tests
All tests files are in the tests folder. To run the test file, head to your docker terminal (make sure the service is running) and enter the following commands
```
cd ../tests
python test.py
```
The file should be able to run smoothly without any errors.

# File structure
This section will explain the file structure of this repository.

```
├── build                          <- folder containing all docker container related files
│   ├── Dockerfile
│   ├── requirements.txt
│   └── docker-compose.yml (volume mount important files)
│
├── notebooks                      <- folder containing test juypter notebooks
│ 
├── src                            <- base folder containing all the main code for each service
│   ├── utils                      <- folder containing any utils file needed (eg. functions for database query etc)
│   │
│   ├── microservice               <- folder containing all python code required in microservices
│   │
│   └── main.py                    <- main python file that consist of all the endpoints for the fastAPI
│
└── tests                          <- folder containing all test files required for each microservice
    └── test.py                    <- python file containing test code to test endpoint
```





