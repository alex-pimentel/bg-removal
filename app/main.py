import base64
import io

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.responses import Response
from PIL import Image
from rembg import remove

app = FastAPI()

@app.post("/remove-bg/")
async def remove_background(
    file: UploadFile = File(...),
    format: str
    | None = Query(None, pattern="^(png)$", description="Return PNG image directly instead of base64 JSON"),
):
    try:
        contents = await file.read()
        input_image = Image.open(io.BytesIO(contents))
        output_image = remove(input_image)
        output_buffer = io.BytesIO()

        if format == "png":
            output_image.save(output_buffer, format="PNG")
            return Response(content=output_buffer.getvalue(), media_type="image/png")
        else:
            output_image.save(output_buffer, format="PNG")
            b64 = base64.b64encode(output_buffer.getvalue()).decode("utf-8")
            return {"image": "data:image/png;base64," + b64}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))