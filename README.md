# MorphoCut Server

This repository contains the MorphoCut web application that serves as a frontend for the [MorphoCut library](https://github.com/morphocut/morphocut).

## Running the development version

During development, Flask and Vue run natively on the host. PostgreSQL and Redis run in their respective Docker containers.

### Prerequisites

- To run PostgreSQL and Redis, you need [Docker Compose](https://docs.docker.com/compose/install/).

- To run the Python application, create a Conda environment by running the following in the repository root:

  ```sh
  conda env create -f environment.yml # Create a prespecified environment
  ```

- To run the Vue application, you need to have [NodeJS](https://nodejs.org/en/download/) installed.  Then install the required packages:

  ```sh
  /$ cd morphocut_server/frontend
  /morphocut_server/frontend/$ npm install # Install all the required packages
  ```

### Run the application

- Start PostgreSQL and Redis. The services will run as long as the window is not closed.

  ```sh
  /$ docker-compose up postgres redis # Start the PostgreSQL and Redis containers exposing the relevant ports
  ```

- In a new window, start Flask:

  ```sh
  /$ source activate_dev # Activate the environment and set appropriate environment variables
  /$ flask run # Run the flask application, reloading automatically as necessary.
  ...
  * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
  ...
  ```

- In a third window, start Vue:

  ```sh
  /$ cd morphocut_server/frontend
  /morphocut_server/frontend/$ npm run serve # Run the Vue frontend, reloading automatically as necessary.
  ...
    App running at:
    - Local:   http://localhost:8080/frontend/ 
  ...
  ```
  
  Open the link to access the application.


## License
This project is licensed under the terms of the MIT license.
