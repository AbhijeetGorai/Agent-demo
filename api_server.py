from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from search_api import SearchAPI
from typing import Optional

# Initialize FastAPI app
app = FastAPI(
    title="Search API",
    description="API to search using Google Serper",
    version="1.0.0"
)

# Create SearchAPI instance
search_api = SearchAPI()

# Request model
class SearchRequest(BaseModel):
    query: str

# Response model
class SearchResponse(BaseModel):
    query: str
    answer: str
    status: str = "success"
    error: Optional[str] = None

@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Search endpoint that takes a query and returns the answer
    """
    try:
        answer = search_api.search(request.query)
        return SearchResponse(
            query=request.query,
            answer=answer
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/")
async def root():
    """
    Root endpoint - health check
    """
    return {"status": "API is running"}

# Run with: uvicorn api_server:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 