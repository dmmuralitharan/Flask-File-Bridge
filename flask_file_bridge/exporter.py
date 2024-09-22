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
    model=None,
    db_source=None,
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

        # get all records
        records = db_source.session.query(model).all()

        data = [record_to_dict(record) for record in records]

        df = pd.DataFrame(data)

        # export selected columns
        if len(selected_columns) > 0:
            df = df[selected_columns]

        # exclude selected columns  
        if len(exclude_columns) > 0:
            df = df.drop(columns=exclude_columns)

        output = BytesIO()

        # export as excel
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

        # export as csv
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


# ----------------------------


# df = pd.DataFrame(result)

#     if 'id' in df.columns:
#         df = df.drop(columns=['id'])

#     desired_order = [
#         'to_store_code', 'to_store_name', 'model_number', 'brand', 'item_name',
#         'last_28_days_sold_qty', 'current_stock', 'demand_quantity',
#         'transfer_quantity', 'yet_to_procure_default', 'yet_to_procure_projected',
#         'projection_days', 'p_approved_flag'
#     ]

#     if all(col in df.columns for col in desired_order):
#         df = df[desired_order]
#     else:
#         return "Missing one or more columns in the DataFrame", 200

#     excel_filename = "REPORT_" + datetime.now().strftime("%Y-%m-%d-%H%M%S") + str(random.randint(100, 999)) + ".xlsx"

#     output = BytesIO()
#     with pd.ExcelWriter(output, engine='openpyxl') as writer:
#         df.to_excel(writer, index=False, sheet_name='Sheet1')

#     output.seek(0)

#     return send_file(output, download_name=excel_filename, as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

# return "Invalid response received", 400
