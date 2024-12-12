# Fault Detection on Milling Machine

This repository contains the code for fault detection on a milling machine using a Lambda Architecture for data processing and real-time monitoring. The system leverages Docker containers to orchestrate various components, ensuring scalable and efficient data handling.

## Table of Contents

- [Introduction](#introduction)
- [Data](#data)
- [Lambda Architecture](#lambda-architecture)
  - [Components](#components)
    - [1. Data Generator](#1-data-generator)
    - [2. Apache Kafka](#2-apache-kafka)
    - [3. Apache Spark](#3-apache-spark)
      - [3.1 Spark Master](#31-spark-master)
      - [3.2 Spark Worker](#32-spark-worker)
      - [3.3 Spark Application](#33-spark-application)
    - [4. Elasticsearch](#4-elasticsearch)
    - [5. Kibana](#5-kibana)
- [Training](#training)
- [Real-time Monitoring](#real-time-monitoring)
- [Installation](#installation)
- [Usage](#usage)
  - [Running the Lambda Architecture](#running-the-lambda-architecture)
  - [Accessing Kibana](#accessing-kibana)
- [Model Deployment](#model-deployment)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Introduction

Fault detection in milling machines is crucial for predictive maintenance, reducing downtime, and optimizing operational efficiency. This project implements a robust system using the Lambda Architecture to process data in real-time and provide actionable insights through visualizations.

## Data

The dataset used for training and evaluation is the **AI4I 2020 Predictive Maintenance Dataset**, available from the [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset). This dataset contains various operational parameters and fault conditions of industrial machinery.

## Lambda Architecture

The Lambda Architecture combines both batch and real-time processing to handle large-scale data efficiently. This implementation uses Docker to containerize and manage the following components:

### Components

#### 1. Data Generator

- **Function:** Generates synthetic data for the milling machine based on the AI4I 2020 dataset.
- **Usage:** Simulates real-time data streams for testing and development purposes.

#### 2. Apache Kafka

- **Function:** Serves as a distributed message broker, facilitating real-time data ingestion and processing.
- **Usage:** Receives data from the Data Generator and streams it to Apache Spark for processing.

#### 3. Apache Spark

Handles real-time data processing through the speed layer.

##### 3.1 Spark Master

- **Function:** Manages the Spark cluster, coordinating tasks and resource allocation.
- **Configuration:** Configured as the master node within the Spark cluster.

##### 3.2 Spark Worker

- **Function:** Executes tasks assigned by the Spark Master, handling data processing workloads.
- **Configuration:** Configured as worker nodes within the Spark cluster.

##### 3.3 Spark Application

- **Function:** Processes incoming data streams in real-time, applies fault detection models, and forwards results to the data store.
- **Usage:** Implements the core logic for fault detection using pre-trained machine learning models.

#### 4. Elasticsearch

- **Function:** Acts as the batch layer, storing processed data for historical analysis and search capabilities.
- **Usage:** Receives data from the Spark Application and indexes it for efficient querying.

#### 5. Kibana

- **Function:** Provides a visualization layer, enabling real-time monitoring and dashboard creation.
- **Usage:** Connects to Elasticsearch to display data insights and fault detection results.

## Training

The fault detection models are trained using machine learning algorithms on the AI4I 2020 dataset. Both **XGBoost** and **CatBoost** classifiers are employed to build robust models capable of identifying various fault conditions.

- **Algorithms Used:**
  - **XGBoost:** An optimized distributed gradient boosting library.
  - **CatBoost:** A gradient boosting library that handles categorical features efficiently.

- **Training Process:**
  1. **Data Preparation:** Preprocess and clean the dataset to ensure quality.
  2. **Model Training:** Train models using cross-validation to evaluate performance.
  3. **Model Evaluation:** Assess models based on accuracy, precision, recall, F1-score, and ROC-AUC.
  4. **Model Saving:** Save the trained models in the `models` folder for deployment.

- **Directory Structure:**
  ```
    ├── LICENSE
    ├── README.md
    ├── data-generator
    │   ├── ai4i2020.csv
    │   ├── generator.py
    │   └── requirements.txt
    ├── docker-compose.yaml
    ├── spark-app
    │   ├── Dockerfile
    │   ├── app.py
    │   ├── models
    │   │   ├── cat_model_HDF.joblib
    │   │   ├── cat_model_Machine failure.joblib
    │   │   ├── cat_model_OSF.joblib
    │   │   ├── cat_model_PWF.joblib
    │   │   ├── cat_model_RNF.joblib
    │   │   ├── cat_model_TWF.joblib
    │   │   ├── xgb_model_HDF.joblib
    │   │   ├── xgb_model_Machine failure.joblib
    │   │   ├── xgb_model_OSF.joblib
    │   │   ├── xgb_model_PWF.joblib
    │   │   ├── xgb_model_RNF.joblib
    │   │   └── xgb_model_TWF.joblib
    │   └── requirements.txt
    └── train
        ├── Dockerfile
        ├── docker-compose.yaml
        └── notebooks
            ├── ai4i2020.csv
            ├── catboost_info
            │   ├── catboost_training.json
            │   ├── learn
            │   │   └── events.out.tfevents
            │   ├── learn_error.tsv
            │   ├── time_left.tsv
            │   └── tmp
            │       ├── cat_feature_index.27341edc-909710fa-5c85a776-1986f402.tmp
            │       ├── cat_feature_index.358d1ad6-7d03d648-6d11d415-550d0161.tmp
            │       ├── cat_feature_index.e3e3eef0-b0ac3e9b-9e44dc5b-84a67f67.tmp
            │       └── cat_feature_index.ec6ec4e9-9a6f6568-82199c4-2be0e543.tmp
            ├── iframe_figures
            │   └── figure_32.html
            ├── main.ipynb
            └── models
                ├── cat_model_HDF.joblib
                ├── cat_model_Machine failure.joblib
                ├── cat_model_OSF.joblib
                ├── cat_model_PWF.joblib
                ├── cat_model_RNF.joblib
                ├── cat_model_TWF.joblib
                ├── xgb_model_HDF.joblib
                ├── xgb_model_Machine failure.joblib
                ├── xgb_model_OSF.joblib
                ├── xgb_model_PWF.joblib
                ├── xgb_model_RNF.joblib
                └── xgb_model_TWF.joblib
  ```

## Real-time Monitoring

Real-time monitoring is achieved using the Elastic Stack (Elasticsearch, Logstash, and Kibana). Processed data is indexed in Elasticsearch and visualized in Kibana dashboards, allowing operators to monitor machine health and detect faults instantaneously.

## Installation

### Prerequisites

- **Docker:** Ensure Docker is installed on your machine. You can download it from [here](https://www.docker.com/get-started).
- **Docker Compose:** Comes bundled with Docker Desktop. Verify installation with:
  ```bash
  docker-compose --version
  ```

### Clone the Repository

```bash
git clone <repository-url>
cd fault_detection
```

## Usage

### Running the Lambda Architecture

1. **Navigate to the Repository Directory:**

   ```bash
   cd fault_detection
   ```

2. **Start the Docker Containers:**

   ```bash
   docker-compose up -d
   ```

   This command initializes all the necessary services defined in the `docker-compose.yml` file:
   - **Data Generator**
   - **Zookeeper**
   - **Kafka**
   - **Spark Master**
   - **Spark Worker**
   - **Spark Application**
   - **Elasticsearch**
   - **Kibana**

3. **Verify Services are Running:**

   ```bash
   docker-compose ps
   ```

   Ensure all services are up and running without errors.

### Accessing Kibana

1. **Open Kibana Dashboard:**

   Navigate to [http://localhost:5601](http://localhost:5601) in your web browser.

2. **Configure Elasticsearch Index:**

   - Go to the **Discover** tab.
   - Select the `milling-data` index to view incoming data.

3. **Create Visualizations and Dashboards:**

   - Use the **Dashboard** tab to create custom visualizations based on the processed data.
   - Monitor real-time fault detection results and machine performance metrics.

### Stopping the Services

To stop all running services:

```bash
docker-compose down
```

## Model Deployment

The trained machine learning models are deployed within the `spark-app` service to facilitate real-time fault detection.

1. **Models Directory:**

   Ensure that the `models` folder contains all the pre-trained model files (`.joblib`).

2. **Spark Application Configuration:**

   The Spark application (`app.py`) loads the models from the `/models` directory and applies them to incoming data streams from Kafka.

3. **Real-time Processing:**

   As data flows through Kafka, Spark processes each data batch, applies the models, and indexes the results in Elasticsearch for visualization.

## Contributing

Contributions are welcome! To contribute:

1. **Fork the Repository.**
2. **Create a Feature Branch:**

   ```bash
   git checkout -b feature/YourFeature
   ```

3. **Commit Your Changes:**

   ```bash
   git commit -m "Add some feature"
   ```

4. **Push to the Branch:**

   ```bash
   git push origin feature/YourFeature
   ```

5. **Open a Pull Request.**

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements

- **AI4I 2020 Predictive Maintenance Dataset:** [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset)
- **Apache Kafka:** [Official Website](https://kafka.apache.org/)
- **Apache Spark:** [Official Website](https://spark.apache.org/)
- **Elasticsearch:** [Official Website](https://www.elastic.co/elasticsearch/)
- **Kibana:** [Official Website](https://www.elastic.co/kibana/)
- **XGBoost:** [Official Documentation](https://xgboost.readthedocs.io/)
- **CatBoost:** [Official Documentation](https://catboost.ai/docs/)