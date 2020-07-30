<h1><p align="center"> PyWren for IBM Cloud </p></h1>

### What is PyWren

[PyWren](https://github.com/pywren/pywren) is an open source project whose goals are massively scaling the execution of Python code and its dependencies on serverless computing platforms and monitoring the results. PyWren delivers the user’s code into the serverless platform without requiring knowledge of how functions are invoked and run.

### PyWren and IBM Cloud

This repository is based on [PyWren](https://github.com/pywren/pywren) main branch and adapted for IBM Cloud Functions and IBM Cloud Object Storage. PyWren for IBM Cloud is not, however, just a mere reimplementation of PyWren’s API atop IBM Cloud Functions. Rather, it is must be viewed as an advanced extension of PyWren. See the complete [design overview](docs/DESIGN.md).

PyWren for IBM Cloud provides great value for the variety of uses cases, like processing data in object storage, running embarrassingly parallel compute jobs (e.g. Monte-Carlo simulations), enriching data with additional attributes and many more. In extending PyWren to work with IBM Cloud Object Storage, we also added a partition discovery component that allows PyWren to process large amounts of data stored in the IBM Cloud Object Storage. See [changelog](CHANGELOG.md) for more details.

### IBM Cloud for Academic institutions

[IBM Academic Initiative](https://ibm.biz/academic) is a special program that allows free trial of IBM Cloud for Academic institutions. This program is provided for students and faculty staff members, and allow up to 12 months of free usage. You can register your university email and get a free of charge account.

## Initial Requirements

* [IBM Cloud Functions account](https://cloud.ibm.com/functions)
* [IBM Cloud Object Storage account](https://www.ibm.com/cloud/object-storage)
* Python >=3.5, <=3.8

## PyWren Setup

1. Install PyWren from the PyPi repository:

    ```bash
    $ pip install pywren-ibm-cloud
    ```

2. Navigate into [config/](config/) and follow the instructions to configure PyWren.

3. Test PyWren by simply running the next command:
  
   ```bash
    $ pywren-ibm-cloud test
   ```

   or by running the next code:

   ```python
   import pywren_ibm_cloud as pywren

   def hello(name):
       return 'Hello {}!'.format(name)

   pw = pywren.ibm_cf_executor()
   pw.call_async(hello, 'World')
   print(pw.get_result())
   ```

## Dataclay runtime
1. Copy dataclay stubs and cfgfiles to current directory
2. Build Docker image with Dataclay
   ```bash
   $ docker build -t dataclay_runtime:2.1 -f pywren-ibm-cloud/runtime/ibm_cf/Dockerfile.dataclay37 .
   ```
3. Create Pywren runtime. Currently only Cloud Functions backend supported
   ```bash
   $ pywren-ibm-cloud runtime create dataclay_runtime:2.1
   ```
4. When calling pywren executor with Map function, use extra_env to initialize dataclay
   ```python
   ...
   pw = pywren.function_executor()
   pw.map(traj_pred_v2_wrapper, idstuples, extra_env = {'PRE_RUN': 'dataclay.api.init'})
   ...
   ```

## Runtime optimizations
   This release contains multiple pywren runtime optimizations. It is required to set following environment variable to point to some local temporary folder, e.g.
   ```bash
   export PYWREN_TEMP_FOLDER=/home/kpavel/pywren-ibm-cloud
   ```

## How to use PyWren for IBM Cloud

The primary object in PyWren is the executor. The standard way to get everything set up is to import `pywren_ibm_cloud`, and call one of the available functions to get a [ready-to-use executor](docs/api-details.md#executor).

The available executors are:

* `ibm_cf_executor()`: IBM Cloud Functions executor.
* `knative_executor()`: Knative executor. See [additional information](docs/knative.md).
* `openwhisk_executor()`: Vanilla OpenWhisk executor. See [additional information](docs/openwhisk.md).
* `local_executor()`: Localhost executor to run functions by using local processes.
* `docker_executor()`: Docker executor to run functions by using processes within a local or remote Docker container.
* `function_executor()`: Generic executor based on the compute backend specified in configuration.

The available calls within an executor are:

|API Call| Type | Description|
|---|---|---|
|[call_async()](docs/api-details.md#executorcall_async) | Async. | Method used to spawn one function activation |
|[map()](docs/api-details.md#executormap) | Async. | Method used to spawn multiple function activations |
|[map_reduce()](docs/api-details.md#executormap_reduce) | Async. | Method used to spawn multiple function activations with one (or multiple) reducers|
|[wait()](docs/api-details.md#executorwait) | Sync. | Wait for the function activations to complete. It blocks the local execution until all the function activations finished their execution (configurable)|
|[get_result()](docs/api-details.md#executorget_result) | Sync. | Method used to retrieve the results of all function activations. The results are returned within an ordered list, where each element of the list is the result of one activation|
|[plot()](docs/api-details.md#executorplot) | Sync. | Method used to create execution plots |
|[clean()](docs/api-details.md#executorclean) | Async. | Method used to clean the temporary data generated by PyWren|

Additional information and examples:

* **Functions**: [PyWren functions and parameters](docs/functions.md)
* **Runtimes**: [Building and managing PyWren runtimes to run the functions](runtime/)
* **Data processing**: [Using PyWren to process data from IBM Cloud Object Storage and public URLs](docs/data-processing.md)
* **Notebooks**: [PyWren on IBM Watson Studio and Jupyter notebooks](examples/hello_world.ipynb)

## Verify - Unit Testing

To test that all is working, use the command:

```bash
$ pywren-ibm-cloud verify
```

or

```bash
$ python -m pywren_ibm_cloud.tests
```

Notice that if you didn't set a local PyWren's config file, you need to provide it as a json file path by `-c <CONFIG>` flag.

Alternatively, for debugging purposes, you can run specific tests by `-t <TESTNAME>`. use `--help` flag to get more information about the test script.

## Additional resources

* [Your easy move to serverless computing and radically simplified data processing](https://conferences.oreilly.com/strata/strata-ny/public/schedule/detail/77226) Strata Data Conference, NY 2019
  * See video of PyWren-IBM usage [here](https://www.youtube.com/watch?v=EYa95KyYEtg&list=PLpR7f3Www9KCjYisaG7AMaR0C2GqLUh2G&index=3&t=0s) and the example of Monte Carlo [here](https://www.youtube.com/watch?v=vF5HI2q5VKw&list=PLpR7f3Www9KCjYisaG7AMaR0C2GqLUh2G&index=2&t=0s)
* [Ants, serverless computing, and simplified data processing](https://developer.ibm.com/blogs/2019/01/31/ants-serverless-computing-and-simplified-data-processing/)
* [Speed up data pre-processing with PyWren in deep learning](https://developer.ibm.com/patterns/speed-up-data-pre-processing-with-pywren-in-deep-learning/)
* [Predicting the future with Monte Carlo simulations over IBM Cloud Functions](https://www.ibm.com/cloud/blog/monte-carlo-simulations-with-ibm-cloud-functions)
* [Process large data sets at massive scale with PyWren over IBM Cloud Functions](https://www.ibm.com/cloud/blog/process-large-data-sets-massive-scale-pywren-ibm-cloud-functions)
* [PyWren for IBM Cloud on CODAIT](https://developer.ibm.com/code/open/centers/codait/projects/pywren/)
* [Industrial project in Technion on PyWren-IBM](http://www.cs.technion.ac.il/~cs234313/projects_sites/W19/04/site/)
* [Serverless data analytics in the IBM Cloud](https://dl.acm.org/citation.cfm?id=3284029) - Proceedings of the 19th International Middleware Conference (Industry)

# Acknowledgements

![image](https://user-images.githubusercontent.com/26366936/61350554-d62acf00-a85f-11e9-84b2-36312a35398e.png)

This project has received funding from the European Union's Horizon 2020 research and innovation programme under grant agreement No 825184.
