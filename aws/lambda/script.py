import boto3
import csv
import io
from datetime import datetime
import os

s3 = boto3.client('s3')

BUCKET_NAME = os.environ.get("BUCKET_NAME", "ulacit-datos-masivos")
INPUT_KEY   = os.environ.get("INPUT_KEY", "input/dataset.csv")
OUTPUT_KEY  = os.environ.get("OUTPUT_KEY", "output/dataset_limpio.csv")

def es_fila_valida(row):
    """
    Valida y normaliza una fila.
    Devuelve (True, fila_normalizada) si es válida,
    o (False, None) si debe descartarse.
    """

    # Copia para no modificar el original
    new_row = dict(row)

    try:
        # 1. Validar y normalizar fecha/hora
        #    Ej: "2009-06-15 17:26:21 UTC" → "2009-06-15 17:26:21"
        fecha_raw = (new_row.get("pickup_datetime") or "").strip()
        if not fecha_raw:
            return False, None

        fecha_raw = fecha_raw.replace(" UTC", "")
        dt = datetime.strptime(fecha_raw, "%Y-%m-%d %H:%M:%S")
        new_row["pickup_datetime"] = dt.strftime("%Y-%m-%d %H:%M:%S")

        # 2. Validar valores numéricos obligatorios
        #    Si alguno está vacío o no se puede convertir → descartar fila

        # fare_amount
        fare_raw = (new_row.get("fare_amount") or "").strip()
        if not fare_raw:
            return False, None
        fare = float(fare_raw)
        new_row["fare_amount"] = str(fare)

        # passenger_count
        pass_raw = (new_row.get("passenger_count") or "").strip()
        if not pass_raw:
            return False, None
        passenger_count = int(float(pass_raw))
        new_row["passenger_count"] = str(passenger_count)

        # longitudes y latitudes
        for col in [
            "pickup_longitude",
            "pickup_latitude",
            "dropoff_longitude",
            "dropoff_latitude"
        ]:
            val_raw = (new_row.get(col) or "").strip()
            if not val_raw:
                return False, None
            val = float(val_raw)
            new_row[col] = str(val)

        # Si llegamos aquí, la fila es válida
        return True, new_row

    except Exception:
        # Cualquier error en conversiones → descartar fila
        return False, None


def lambda_handler(event, context):
    # 1. Leer archivo original desde S3
    obj = s3.get_object(Bucket=BUCKET_NAME, Key=INPUT_KEY)
    data = obj["Body"].read().decode("utf-8").splitlines()

    reader = csv.DictReader(data)
    fieldnames = reader.fieldnames

    output_buffer = io.StringIO()
    writer = csv.DictWriter(output_buffer, fieldnames=fieldnames)
    writer.writeheader()

    filas_totales = 0
    filas_validas = 0

    # 2. Procesar fila por fila
    for row in reader:
        filas_totales += 1
        es_valida, fila_limpia = es_fila_valida(row)
        if es_valida and fila_limpia:
            writer.writerow(fila_limpia)
            filas_validas += 1
        # si no es válida, simplemente se omite

    # 3. Guardar archivo limpio en S3
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=OUTPUT_KEY,
        Body=output_buffer.getvalue()
    )

    return {
        "status": "OK",
        "bucket": BUCKET_NAME,
        "input_key": INPUT_KEY,
        "output_key": OUTPUT_KEY,
        "filas_totales": filas_totales,
        "filas_validas": filas_validas,
        "filas_descartadas": filas_totales - filas_validas
    }
