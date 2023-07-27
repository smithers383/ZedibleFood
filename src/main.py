import tempfile
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
import zipfile
import os
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
    output_dir = os.path.join(tmpdir.name, 'output')
    os.mkdir(output_dir)

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

    zed = Zedible()
    zed.supplierFile.delete("1.0", "end")
    zed.supplierFile.insert("1.0", f"{output_dir}/1")
    zed.load_web_files(files)
    zed.process_data()

    print(output_dir)

    output_zip = f"{tmpdir.name}/output.zip"

    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for folder_name, subfolders, filenames in os.walk(output_dir):
            print(filenames)
            for filename in filenames:
                file_path = os.path.join(folder_name, filename)
                relative_path = os.path.relpath(file_path, output_dir)
                zipf.write(file_path, arcname=relative_path)

    try:
        return StreamingResponse(open(output_zip, "rb"), media_type="application/zip")
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
