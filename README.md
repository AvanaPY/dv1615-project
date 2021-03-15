# Project for BTH course DV1615 by Emil Karlström

## TODO:
* Change threshold to 99%

## How to run

Clone the repository and create a virtual environment using 
```python 
python -m venv env
``` 
and running 
```python 
pip install -r requirements.txt
``` 
to get download all the required libraries.

After having installed the libraries create a file in the root directory called `.env` and add the variables:
* COGNITIVE_API_HEADER_VAL: Your API key for the API Management layer
* API_MANAGEMENT_URL: The URL to the API Management Layer for the Azure Cognitive Services
* LAGER_API_URl: The URL to the lager-api part of the assignment

### .env Example 

```makefile
COGNITIVE_API_HEADER_KEY = beicz80nvnvp5zs2tijmmt0gvugqnkfz
API_MANAGEMENT_URL       = https://dv1615-apimanagement-lab.azure-api.net
LAGER_API_URl            = https://www.lager-api-by-docker-container.net/
```
NOTE:
The `COGNITIVE_API_HEADER_KEY` key above is randomly generated and the real one should be acquried from the project's page on Canvas.