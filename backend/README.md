# 🚀 FastAPI with Hot Reload via Docker Compose

This project sets up a FastAPI application with hot reload support using Docker and Docker Compose.

## 📁 Structure

```
fastapi_hot_reload/
├── app/
│   └── main.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 🛠️ Usage

0. create share network 

```bash
docker network create shared_network
```

1. Build and start the container:

```bash
docker-compose up -d --build
```

```bash
docker-compose exec prod_fastapi_hot_reload_sample  bash
```

2. Visit [http://localhost:8001](http://localhost:8001) to test if the server is running correctly. You will get 
```bash
{"message":"home page"}
```

3. Modify `main.py` and refresh the browser to see changes instantly.


## 📦 Dependencies

available in requirements.txt

## Bash into container 

### bash as root

```bash 
docker-compose exec --user root prod_fastapi_hot_reload_sample bash
```
### bash as appuser
```bash
docker-compose exec prod_fastapi_hot_reload_sample bash
```

## Sample authentication
### generate token 
```bash
curl --location --request POST 'http://localhost:8001/token' \
--form 'username="johndoe"' \
--form 'password="secret"'
```
#### response:
```bash
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzU5OTM3NzYzfQ.DDhoQXknJHK9pWX527M6BZWf8s5Lbc0U6JeJOGxNjgw",
    "token_type": "bearer"
}
```

### validate token
```bash
curl --location --request GET 'http://localhost:8001/validate-token' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzYyNzkxMDgzfQ._X5RTuHmrX4pHEKn1kVYKYfxl9IRpBjIA1IrB9Cf3Z4'
```
#### response: 
```bash
{
    "message": "you are now authenticated",
    "user": "johndoe"
}
```
