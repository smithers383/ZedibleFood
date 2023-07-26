import tempfile
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
import zipfile
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
    tmpdir = tempfile.TemporaryDirectory()

    files = [
        autoProduct,
        supplier,
        master,
        userDB,
        default_percentagaes,
        autoCategory
    ]

    for file in files:
        file_location = f"{tmpdir.name}/{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())
        file.tmp = file_location

    Zedible.load_web_files(Zedible, files)
    # Zedible.process_data(Zedible)

    output = f"{tmpdir.name}/output.zip"

    with zipfile.ZipFile(output, 'w') as zipf:
        for file in files:
            zipf.write(f"{tmpdir.name}/{file.filename}")

    try:
        return StreamingResponse(open(output, "rb"), media_type="application/zip")
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))



@app.get("/")
async def main():
    content = """
<body>
    <form action="/upload" enctype="multipart/form-data" method="post">
        <div>
            <label for="master">Main Database File</label>
            <p>
                Comma seperated file with 5 columns: Kategorie, Name DE, Name EN, CO2 / 1.6FU (ohne Flug), kg CO2 / kg (ohne Flug).
                <br>
                The file should have a headerline.
            </p>
            <input id=master name="master" type="file" required>
        </div>
        <hr>
        
        <div>
            <label for="userDB">Substitutions Database File</label>
            <p>
                Comma seperated file with 2 columns: Supplier Database Name EN, Main Database Name EN.
                <br>
                The file must have a headerline.
            </p>
            <input id=userDB name="userDB" type="file" required>
        </div>
        <hr>
        
        <div>
            <label for="supplier">Supplier Database File</label>
            <p>
                Comma seperated file with 5 columns: Supplier, Product Code, Product Name, Case Size, Ingredients.
                <br>
                The file must have a headerline.
            </p>
            <input id=supplier name="supplier" type="file" required>
        </div>
        <hr>

        <div>
            <label for="default_percentagaes">Default Percentages File</label>
            <p>
                Comma seperated file with 3 columns: E Number, Name EN and Fraction.
                <br>
                The file must have a headerline.
            </p>
            <input id=default_percentagaes name="default_percentagaes" type="file" required>
        </div>
        <hr>
        
        <div>
            <label for="autoProduct">Automatic Sub-ingredient file</label>
            <p>
                Comma seperated file with 3 columns: List of ingredients to replace,CO2 to use and Main DB name.
                <br>
                The file must have a headerline. The list of ingredients needs to be semicolon (;) seperated
            </p>
            <input id=autoProduct name="autoProduct" type="file" required>
        </div>
        <hr>
        
        <div>
            <label for="autoCategory">Reference Supplier Product to Category Matching File</label>
            <p>
                Comma seperated file with 6 columns: Supplier, Product Code, Product Name, Case Size, Ingredients and Category.
                <br>
                The file must have a headerline.
            </p>
            <input id=autoCategory name="autoCategory" type="file" required>
        </div>
        <hr>


        <input type="submit" value="Go">
    </form>
</body>
    """
    return HTMLResponse(content=content)
