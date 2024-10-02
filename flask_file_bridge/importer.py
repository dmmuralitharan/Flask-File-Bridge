from operator import and_
from flask import request, jsonify
import pandas as pd

from datetime import datetime
import os


def import_data(
    db_source=None,
    model=None,
    file_by_form=None,
    drop_duplicates=False,
    format="excel",
    sheet_name_or_index=0,
    save_path="uploaded_files/",
    extra_form_columns=[],
    selected_columns=[],
    exclude_columns=[],
    delete_all_and_import=False,
    delete_by_columns_and_import=[],
):

    try:
        file = request.files[file_by_form]

        if file:

            # Save The File In Server
            if not os.path.exists(save_path):
                os.makedirs(save_path)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            file_name, file_extension = os.path.splitext(file.filename)
            new_file_name = f"{file_name}_{timestamp}{file_extension}"

            final_save_path = os.path.join(save_path, new_file_name)
            file.save(final_save_path)

            file.seek(0)

            # Read The Excel File
            if format.lower() == "excel":

                df = pd.read_excel(
                    file, sheet_name=sheet_name_or_index, engine="openpyxl"
                )

            # Read The CSV File
            elif format.lower() == "csv":
                if os.stat(final_save_path).st_size == 0:
                    return jsonify({"message": "CSV file is empty", "status": 0})

                df = pd.read_csv(file)

            else:
                return jsonify(
                    {"message": "Incorrect Format ~ Try Excel or CSV", "status": 0}
                )

            # Import Selected Columns
            if len(selected_columns) > 0:
                df = df[selected_columns]

            # Exclude Selected Columns
            if len(exclude_columns) > 0:
                df = df.drop(columns=exclude_columns)

            # Add The Extra Columns From Data
            if len(extra_form_columns) > 0:
                for extra_form_column in extra_form_columns:

                    extra_form_value = request.form.get(extra_form_column)

                    if extra_form_column not in df.columns:
                        df[extra_form_column] = extra_form_value
                    else:
                        df[extra_form_column] = extra_form_value

            # Change N/A Value And Empty Cells As None
            df = df.where(pd.notnull(df), None)

            # Drop Duplicates
            if drop_duplicates == True:
                df = df.drop_duplicates()

            # Delete All Data In DB and Import From Excel/CSV
            if delete_all_and_import == True:
                db_source.session.query(model).delete(synchronize_session=False)
                db_source.session.flush()
            
            elif delete_all_and_import and len(delete_by_columns_and_import) > 0:
                return jsonify({"message": "Please choose only one option: `delete_all_and_import` or `delete_by_columns_and_import`", "status": 0})

            # Bulk Import
            bulk_insert = []

            for index, row in df.iterrows():
                record = model(**row.to_dict())
                bulk_insert.append(record)

                # Delete The Rows By Columns In DB and Import From Excel/CSV
                if len(delete_by_columns_and_import) > 0:

                    for col in delete_by_columns_and_import:
                        if col not in df.columns:
                            return jsonify({"message": f"Column '{col}' not found in file", "status": 0})
                        
                    filter_condition = []
                    
                    for col in delete_by_columns_and_import:
                        value = row[col]
                        filter_condition.append(getattr(model, col) == value)
                    
                    db_source.session.query(model).filter(*filter_condition).delete(synchronize_session=False)
                    db_source.session.flush() 

            db_source.session.bulk_save_objects(bulk_insert)
            db_source.session.commit()

            inserted_count = len(bulk_insert)

            return jsonify(
                {
                    "message": f"{inserted_count} Records Imported Successfully ",
                    "status": 1,
                }
            )

        else:
            return jsonify({"message": "File Not Found", "status": 0})

    except Exception as e:
        return jsonify({"message": str(e), "status": 0})
