from io import BytesIO
from flask import jsonify, send_file
import pandas as pd
from sqlalchemy.inspection import inspect


def record_to_dict(record):
    return {
        column.key: getattr(record, column.key)
        for column in inspect(record).mapper.column_attrs
    }


def export_data(
    db_source=None,
    model=None,
    exporting_format="Excel",
    output_filename="exported_data",
    selected_columns = [],
    exclude_columns = [],
):

    if model is None or db_source is None:
        return (
            jsonify({"message": "Model and database source are required", "status": 0}),
            400,
        )

    try:

        # Get All Records
        records = db_source.session.query(model).all()

        data = [record_to_dict(record) for record in records]

        df = pd.DataFrame(data)

        # Export Selected Columns
        if len(selected_columns) > 0:
            df = df[selected_columns]

        # Exclude Selected Columns  
        if len(exclude_columns) > 0:
            df = df.drop(columns=exclude_columns)

        output = BytesIO()

        # Export As Excel
        if exporting_format.lower() == "excel":
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Sheet1")

            output.seek(0)

            return send_file(
                output,
                download_name=f"{output_filename}.xlsx",
                as_attachment=True,
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        # Export As CSV
        elif exporting_format.lower() == "csv":

            df.to_csv(output, index=False)

            output.seek(0)

            return send_file(
                output,
                download_name=f"{output_filename}.csv",
                as_attachment=True,
                mimetype="text/csv",
            )

        else:
            return jsonify(
                {"message": "Incorrect Format ~ Try Excel or CSV", "status": 0}
            )

    except Exception as e:
        return jsonify({"message": str(e), "status": 0})

