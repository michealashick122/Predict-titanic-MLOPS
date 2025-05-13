FROM astrocrpublic.azurecr.io/runtime:3.0-1

RUN pip install --no-cache-dir \
    apache-airflow-providers-google \
    apache-airflow-providers-postgres \
    psycopg2-binary \
    sqlalchemy \
    pandas