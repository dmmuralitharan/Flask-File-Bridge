
# Flask-File-Bridge

**Flask-File-Bridge** is a lightweight library that simplifies the process of importing and exporting data from Excel and CSV files using Flask and SQLAlchemy ORM. This package is ideal for developers who need to handle bulk data uploads, manipulate the data, and insert it into a database, or export data from a database to Excel or CSV files in their Flask applications.

## Features

- Import data from Excel and CSV files into your Flask app's database.
- Export data from your database as Excel or CSV files.
- Handle duplicate records, extra columns, and flexible column selection during imports and exports.
- Works seamlessly with Flask and Flask-SQLAlchemy ORM.
  
## Installation

To install Flask-File-Bridge, you can use `pip`:

```bash
pip install Flask-File-Bridge
```

Alternatively, you can install it directly from the source:

```bash
git clone https://github.com/dmmuralitharan/Flask-File-Bridge.git
cd Flask-File-Bridge
python setup.py install
```

## Dependencies

- Flask
- Flask-SQLAlchemy
- pandas
- openpyxl

You can install these dependencies via `pip`:

## Usage

### 1. Importing Data

Use the `import_data` function to import data from Excel or CSV files into your database.

#### Parameters:
- `db_source`: SQLAlchemy database instance.
- `model`: The SQLAlchemy model class to which the data will be inserted.
- `file_by_form`: The form field name used to upload the file.
- `drop_duplicates`: Boolean to indicate whether to drop duplicate rows.
- `format`: The format of the file (`excel` or `csv`).
- `sheet_name_or_index`: Sheet name or index for Excel files.
- `save_path`: The directory where the uploaded file will be saved.
- `extra_form_columns`: Additional columns to be added from form data.
- `selected_columns`: List of columns to be selected from the file.
- `exclude_columns`: List of columns to be excluded from the file.
- `delete_all_and_import`: The delete all and import used to delete all data in DB table and import new data from file. 
- `delete_by_columns_and_import`: List of columns filters to delete matching records in the database before importing.

#### Example:

```python
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_file_bridge import import_data

app = Flask(__name__)
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

@app.route("/upload", methods=["POST"])
def upload_file():
    return import_data(
        db_source=db,
        model=User,
        file_by_form="file",
        drop_duplicates=True,
        format="excel",
        sheet_name_or_index=0,
        save_path="uploads/",
        extra_form_columns=["status"],
        selected_columns=["username", "email"],
        exclude_columns=["id"],
        delete_all_and_import=False,
        delete_by_columns_and_import=["username"]
    )

if __name__ == "__main__":
    app.run(debug=True)
```

### 2. Exporting Data

Use the `export_data` function to export data from your database to an Excel or CSV file.

#### Parameters:
- `db_source`: SQLAlchemy database instance.
- `model`: The SQLAlchemy model class to be exported.
- `exporting_format`: The format of the exported file (`excel` or `csv`).
- `output_filename`: The name of the output file.
- `selected_columns`: List of columns to be included in the export.
- `exclude_columns`: List of columns to be excluded from the export.

#### Example:

```python
from flask import Flask, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_file_bridge import export_data

app = Flask(__name__)
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

@app.route("/export", methods=["GET"])
def export_users():
    return export_data(
        db_source=db,
        model=User,
        exporting_format="csv",
        output_filename="users_export",
        selected_columns=["username", "email"],
        exclude_columns=["id"]
    )

if __name__ == "__main__":
    app.run(debug=True)
```

## Import Data Workflow

1. **File Upload**: The file is uploaded through a form, saved to a specified directory on the server.
2. **Data Handling**: The data is read from the file, filtered by selected or excluded columns, extra form data is added if needed, and duplicates are optionally removed.
3. **Database Insertion**: The data is converted into the appropriate SQLAlchemy model objects and bulk-inserted into the database.

## Export Data Workflow

1. **Data Retrieval**: The data is retrieved from the database based on the specified SQLAlchemy model.
2. **Data Processing**: Selected columns are exported, or excluded columns are dropped from the final output.
3. **File Generation**: The data is written into a new file (Excel or CSV) and returned as a downloadable attachment.

## Contributing

If you'd like to contribute, please fork the repository and submit a pull request. Any contributions, including bug fixes, new features, or documentation improvements, are welcome.

1. Fork the repo.
2. Create your feature branch (`git checkout -b feature/your-feature-name`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/your-feature-name`).
5. Open a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/dmmuralitharan/Flask-File-Bridge/blob/master/LICENSE) file for details.
