# Satiscribble-AI
This is the repository for Satiscribble AI. This python server is hosted with fastAPI and contains all the AI microservices needed for satiscribble.

# Setup
This github is hosted on Docker. To set up your docker image, please follow the following steps after you git clone.
```
cd build
docker compose up
```
Afterwhich, enter the docker container terminal and run `uvicorn main:app --port=8000 --host=0.0.0.0` to start the service.

# File structure
This section will explain the file structure of this repository.

```
├── build                          <- folder containing all docker container related files
│   ├── Dockerfile
│   ├── requirements.txt
│   └── docker-compose.yml (volume mount important files)
│
├── src                            <- base folder containing all the main code for each service
│   ├── utils                      <- folder containing any utils file needed (eg. functions for database query etc)
│   │
│   ├── helper                     <- folder containing all python code required in microservices
│   │
│   └── main.py                    <- main python file that consist of all the endpoints for the fastAPI
│
└── tests                          <- folder containing all test files required for each microservice
    └── test.py                    <- python file containing test code to test endpoint
```





