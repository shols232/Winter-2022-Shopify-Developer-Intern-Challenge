# Winter 2022 -  Shopify Developer Intern Challenge

## About
This is the solution to the winter 2022 Shopify intern challenge. An image repository api providing endpoints to users for several features.

### Requirements
python 3.8 and above.

### How to install
After cloning this repository.
First create a virtualenv using `python3 -m venv venv`
Then activate your vitual environment with  `source venv/bin/activate` if on linux.
- Next   
```python
cd imagerepo
pip install -r requirements.txt
```
- change .env.example to .env and fill in your environment variables
- Now run
```python
python manage.py migrate
```

### Tests
in your teminal, run `pytest` to run the tests.

### Run Server
```python 
python manage.py runserver
```
the server should now be running at `http://127.0.0.1:8000`

### Swagger Docs For the API
Open the Swagger Docs to see all the available endpoints
`http://127.0.0.1:8000/api/docs/redoc/`
  


### A brief of the basic API Endpoints.

- `http://127.0.0.1:8000/api/auth/register/` ---> POST
```python
  {
    'username': your_username, 
    'password': your_password
  }
``` 
- RESPONSE ---> `{token: token_string # USE THIS TOKEN FOR AUTHORIZATION }` 
- use the token with this format under Headers  ---> `Authorization : 'Token your_token_string'`

- `http://127.0.0.1:8000/api/auth/login/` ---> POST 
```python
    {
    'username': your_username, 
    'password': your_password
    }
``` 
- RESPONSE ---> `{token: token_string # USE THIS TOKEN FOR AUTHORIZATION }` 
- use the token with this format under Headers  ---> `Authorization : 'Token your_token_string'`

**All endpoints below should be sent with Authorization Header token already set. Use POSTMAN.**

- `http://127.0.0.1:8000/api/images/add/` ---> POST
- ```python
    {
        'image': any_image_less_than_2mb, 
        'private': true/false  # private is an Optional parameter which defaults to false
    }
    ```
- **Note: To send multiple images simply select multiple images on postman, or add multiple `image` parameters containing the different images you wish to add.**

- `http://127.0.0.1:8000/api/images/my_images/` ---> GET
    - Get all images which you own, both private and public.

- `http://127.0.0.1:8000/api/images/search/` ---> GET
    - Search for mages by name. Images you don't own will also be shown, unless they were uploaded as private images.
        - name : query_parameter used to search for the image

- `http://127.0.0.1:8000/api/images/share/` ---> POST
    - Share images to other users. Only images you own can be shared.
        - target_user : username of the user that the image should be shared to.
        - image_name : name of the image you own.

**Ensure to check the redoc api to get a more comprehensive detailing on the API features.**