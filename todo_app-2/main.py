from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from opentracing.ext import tags
from opentracing.propagation import Format
from jaeger_client import Config
import os
import logging
from dotenv import load_dotenv

from routers.todo_router import router as todo_router

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(
    title="ToDo API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def init_tracer():
    config = Config(
        config={
            'sampler': {'type': 'const', 'param': 1},
            'local_agent': {
                'reporting_host': os.getenv('JAEGER_AGENT_HOST', 'jaeger'),
                'reporting_port': int(os.getenv('JAEGER_AGENT_PORT', '6831')),
            },
            'logging': True,
        },
        service_name='todo-api',
        validate=True,
    )
    return config.initialize_tracer()

tracer = init_tracer()

app.include_router(todo_router, prefix="/api")

@app.middleware("http")
async def tracing_middleware(request, call_next):
    span_ctx = tracer.extract(
        Format.HTTP_HEADERS,
        request.headers
    )
    
    span = tracer.start_span(
        operation_name=f"{request.method} {request.url.path}",
        child_of=span_ctx
    )
    
    span.set_tag(tags.HTTP_METHOD, request.method)
    span.set_tag(tags.HTTP_URL, str(request.url))
    
    try:
        response = await call_next(request)
        span.set_tag(tags.HTTP_STATUS_CODE, response.status_code)
        return response
    except Exception as e:
        span.set_tag(tags.ERROR, True)
        span.set_tag("error.message", str(e))
        raise
    finally:
        span.finish()

@app.get("/")
def read_root():
    return {"message": "Todo API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)