from flask import request, jsonify
import pandas as pd

from datetime import datetime
import os


def import_data(
    file_by_form=None,
    # file_path=None,
    save_path="uploaded_files/",
    format="excel",
    sheet_name_or_index=0,
    db_source=None,
    model=None,
    drop_duplicates=True,
    extra_form_columns = [],
    selected_columns = [],
    exclude_columns = [],
):

    try:
        file = request.files[file_by_form]

        if file:

            # save the file in server
            if not os.path.exists(save_path):
                os.makedirs(save_path)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            file_name, file_extension = os.path.splitext(file.filename)
            new_file_name = f"{file_name}_{timestamp}{file_extension}"

            final_save_path = os.path.join(save_path, new_file_name)
            file.save(final_save_path)

            file.seek(0)
            
            # read the excel file
            if format.lower() == "excel":

                df = pd.read_excel(
                    file, sheet_name=sheet_name_or_index, engine="openpyxl"
                )

            # read the csv file
            elif format.lower() == "csv":
                if os.stat(final_save_path).st_size == 0:
                    return jsonify({"message": "CSV file is empty", "status": 0})

                df = pd.read_csv(file)

            else:
                return jsonify(
                    {"message": "Incorrect Format ~ Try Excel or CSV", "status": 0}
                )
            
            # import selected columns
            if len(selected_columns) > 0:
                df = df[selected_columns]

            # exclude selected columns  
            if len(exclude_columns) > 0:
                df = df.drop(columns=exclude_columns)
            
            # add the extra columns from form data
            if len(extra_form_columns) > 0:
                for extra_column in extra_form_columns:

                    extra_value = request.form.get(extra_column)

                    if extra_column not in df.columns:
                        df[extra_column] = extra_value  
                    else:
                        df[extra_column] = extra_value

            # change N/A value and empty cells as None
            df = df.where(pd.notnull(df), None)

            # drop duplicates
            if drop_duplicates == True:
                df = df.drop_duplicates()

            # bulk import
            bulk_insert = []

            for index, row in df.iterrows():
                record = model(**row.to_dict())
                bulk_insert.append(record)

            db_source.session.bulk_save_objects(bulk_insert)
            db_source.session.commit()

            inserted_count = len(bulk_insert)
            
            return jsonify(
                {"message": f"{inserted_count} Data Imported Successfully ", "status": 1}
            )

        else:
            return jsonify({"message": "File Not Found", "status": 0})

    except Exception as e:
        return jsonify({"message": str(e), "status": 0})
