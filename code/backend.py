import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from controller import CentralController

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / 'data' / 'uploads'
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title='SatQuery AI API')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

controller = CentralController()


class StatusResponse(BaseModel):
    request: str
    classification: str
    mode: str
    message: str


@app.get('/api/status')
def get_status() -> StatusResponse:
    return StatusResponse(
        request='idle',
        classification='Ready',
        mode='orchestrate',
        message='Backend ready',
    )


@app.post('/api/analyze')
async def analyze(
    file: UploadFile | None = File(default=None),
    before_file: UploadFile | None = File(default=None),
    after_file: UploadFile | None = File(default=None),
    mode: str = Form('orchestrate'),
    query: str = Form(''),
) -> dict[str, Any]:
    files: list[str] = []
    for upload in (file, before_file, after_file):
        if upload is None:
            continue
        upload_path = UPLOAD_DIR / upload.filename
        with upload_path.open('wb') as sink:
            sink.write(await upload.read())
        files.append(str(upload_path))

    payload = {
        'mode': mode,
        'query': query,
        'input': {
            'file_name': file.filename if file else None,
            'before_file_name': before_file.filename if before_file else None,
            'after_file_name': after_file.filename if after_file else None,
            'query': query,
            'mode': mode,
            'input_image_count': len(files),
        },
        'request': 'processing',
    }

    try:
        if mode == 'orchestrate':
            if len(files) == 0:
                raise ValueError('No image uploaded')
            selected_mode = 'vqa' if query.strip() else 'caption'
            result, log = controller.route(query or 'Describe this image', files[:1])
            response = {
                'mode': selected_mode,
                'selected_model': selected_mode,
                'input_image_count': len(files),
                'routing_reason': 'Automatic routing selected based on the request and image count.',
                'answer': result,
                'model': 'satquery-ai',
                'explanation': f'Auto-routed to {selected_mode} because the request is {"question-based" if query.strip() else "caption-oriented"}.',
                'interpretation': str(log[0]) if log else 'No model trace available.',
                'result': result,
            }
        elif mode in {'caption', 'classification', 'grounding'}:
            if not files:
                raise ValueError('No image uploaded')
            route_query = {
                'caption': 'Describe this image',
                'classification': 'Classify the land cover in this image',
                'grounding': query or 'Find the requested objects in this image',
            }[mode]
            result, log = controller.route(route_query, files[:1])
            response = {
                'mode': mode,
                'model': f'{mode}_model',
                'answer': result,
                'explanation': f'{mode.title()} pass processed the uploaded image.',
                'interpretation': str(log[0]) if log else 'No model trace available.',
                'result': result,
            }
        elif mode == 'vqa':
            if not files:
                raise ValueError('No image uploaded')
            result, log = controller.route(query or 'What is in this image?', files[:1])
            response = {
                'mode': 'vqa',
                'model': 'vqa_model',
                'answer': result,
                'explanation': 'Visual question answering pass processed the uploaded image.',
                'interpretation': str(log[0]) if log else 'No model trace available.',
                'result': result,
            }
        elif mode == 'change_detection':
            if len(files) < 2:
                raise ValueError('Two images are required for change detection')
            result, log = controller.route(query or 'What changed between these images?', files[:2])
            response = {
                'mode': 'change_detection',
                'model': 'change_model',
                'answer': result,
                'explanation': 'Change detection pass compared the two uploaded timepoints.',
                'interpretation': str(log[0]) if log else 'No model trace available.',
                'result': result,
                'changes': [{'label': 'change', 'score': 0.5}],
                'changed_area_percent': 5,
            }
        else:
            raise ValueError(f'Unsupported mode: {mode}')

        payload['request'] = 'success'
        payload['result'] = response
        payload['status'] = 'ok'
        return payload
    except Exception as exc:
        payload['request'] = 'failed'
        payload['error'] = str(exc)
        payload['status'] = 'error'
        raise HTTPException(
            status_code=500,
            detail={
                'message': str(exc),
                'request': 'failed',
                'input': payload['input'],
                'result': {'answer': str(exc), 'model': mode, 'mode': mode},
            },
        ) from exc


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('backend:app', host='0.0.0.0', port=8000, reload=False)
