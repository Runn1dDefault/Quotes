# Quotes API

Running requires:
* Python 3.11 (tested under Python 3.11.2)

---
### Setting up Before the beginning
#### Create .env file in base directory and populate it like .env-example
> :warning: **Required!**
```text
    .
    ├── ...
    ├── Quotes
>>> │   ├── .env      
    │   ├── .env-example          
    │   ├── docker-compose.yml
    │   └── ...
    └── ...
```
#### Local running
###### Installing Dependencies
```bash
pip install -r requirements.txt
```
###### Making migrations
```bash
python manage.py makemigrations
```
```bash
python manage.py migrate
```
###### Server running
```bash
python manage.py runserver
```
---
### Running with docker containers 
###### Config 
```bash
docker-compose config
```

###### Build
```bash
docker-compose up -d --build
```
###### View containers
```bash
docker-compose ps
```
###### Logs
```bash
docker-compose logs -f 
```
###### Stop and Down
> :warning: **`-v` flag will remove volumes!**
```bash
docker-compose down -v
```
---

GOOD LUCK!