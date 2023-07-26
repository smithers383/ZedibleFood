from typing import List

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from typing_extensions import Annotated

from Zedible import App as Zedible
app = FastAPI()

@app.post("/upload")
async def create_upload_files(
    autoProduct: UploadFile = File(),
    supplier: UploadFile = File(),
    master: UploadFile = File(),
    userDB: UploadFile = File(),
    default_percentagaes: UploadFile = File(),
    autoCategory: UploadFile = File()
):
    files = [
        autoProduct.file,
        supplier.file,
        master.file,
        userDB.file,
        default_percentagaes.file,
        autoCategory.file
    ]

    Zedible.load_web_files(Zedible, files)
    Zedible.process_data(Zedible)


    return {"files": files}

@app.get("/")
async def main():
    content = """
<body>
<form action="/upload" enctype="multipart/form-data" method="post">

<label for="autoProduct">harvey</label>
<input id=autoProduct name="autoProduct" type="file">
<br>

<label for="supplier">supplierdb</label>
<input id=supplier name="supplier" type="file">
<br>

<label for="master">master</label>
<input id=master name="master" type="file">
<br>

<label for="userDB">substitutions</label>
<input id=userDB name="userDB" type="file">
<br>

<label for="default_percentagaes">default</label>
<input id=default_percentagaes name="default_percentagaes" type="file">
<br>

<label for="autoCategory">cat.xlsx</label>
<input id=autoCategory name="autoCategory" type="file">
<br>


<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)



# plan:
#   - add fastapi to the repo and create an endpoint and form that can be exposed
#   - create another method on the "App" class to allow for files to be loaded from the form request
#   - handle errors with uploads
#   - provision ec2 instance (size tbc)
#   - configure ec2 with python/uvicorn/nginx with basic auth
#   - configure s3 output or increase timeout - async? progress? s3 event?