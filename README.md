# Message Service

This is a REST API service for sending, fetching and deleting messages.

## Setup and Run

Clone the git repository and move into the project directory

```bash
git clone https://github.com/PhNorberg/OSTTRA.git
```
```
cd OSTTRA
```
Build and run the service

```
docker compose build
```
```
docker compose up -d
```

## Using the service

You can interact with the service through your **terminal** using `curl` commands or via the **Swagger UI web interface**.


### **Terminal Usage**

#### **Base URL**
```
http://localhost:8000/api
```

#### **Submit A Message**

*Send a message to a recipient.*

- **Endpoint:** `POST /api/messages`
- **Required Fields:**
  - `to_user`: string
  - `message`: string 
- **Example Request**

```
curl -X POST "http://localhost:8000/api/messages" \
-H "Content-Type: application/json" \
-d '{"to_user": "Gary Gensler", "message": "Happy retirement!"}'
```

#### **Fetch New Messages**

*Retrieve all unread messages*

- **Endpoint:** `GET /api/messages/new`
- **Example Request:**

```
curl -X GET "http://localhost:8000/api/messages/new"
```

#### **Fetch Messages by Index Range**

*Retrieve messages between specific start and stop indices.*

- **Endpoint:** `GET /api/messages`
- **Query Parameters:** 
  - `start`: integer
  - `stop`: integer 
- **Example Request**
```
curl -X GET "http://localhost:8000/api/messages?start=1&stop=2"
```

#### **Delete Messages**

*Delete one or more messages.*

- **Endpoint:** `DELETE /api/messages`
- **Required Fields:** 
  - `ids`: List of integers
- **Example Request:**

```
curl -X DELETE "http://localhost:8000/api/messages" \
-H "Content-Type: application/json" \
-d '{"ids" : [1, 2]}'
```

### **Swagger UI**

If you prefer a web interface, below is the Swagger UI endpoint. Swagger UI allows you to view all available endpoints and their descriptions, aswell as interact with them by providing the required parameters. Simply open your browser, navigate to this URL, and interact with the API endpoints there. 
```
http://localhost:8000/docs
```
For more details on how to use Swagger UI, check the official documentation:
[Swagger UI Documentation](https://swagger.io/tools/swagger-ui/)
