# SHL Assessment Recommender

This project is a FastAPI-based conversational SHL assessment recommender.

The chatbot takes a user's hiring requirement and recommends suitable SHL assessments from a local catalog.

## Features

- Health check endpoint
- Chat endpoint
- SHL catalog-based recommendations
- Clarification for vague queries
- Off-topic refusal
- Comparison between assessments

## API Endpoints

### GET /health

Returns:

json
{
  "status": "ok"
}

POST /chat

Request:

{
  "messages": [
    {
      "role": "user",
      "content": "I am hiring a Python developer"
    }
  ]
}

Response:

{
  "reply": "Based on your requirement, I found suitable SHL assessment(s).",
  "recommendations": [
    {
      "name": "Python (New)",
      "url": "https://www.shl.com/products/product-catalog/view/python-new/",
      "test_type": "K"
    }
  ],
  "end_of_conversation": true
}

## Tech Stack

Python

FastAPI

Uvicorn

JSON catalog


## How to Run Locally

### Install dependencies:

pip install -r requirements.txt

### Run the API:

uvicorn main:app --reload

### Open Swagger UI:

http://127.0.0.1:8000/docs

## Project Files

1. main.py
2. catalog.json
3. requirements.txt
4. README.md