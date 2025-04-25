# Usa la imagen base oficial de AWS para Python
FROM public.ecr.aws/lambda/python:3.10

# Copia el código de tu app (asegúrate de tener src/ con el código)
COPY src/ ${LAMBDA_TASK_ROOT}

# Instala dependencias (requirements.txt debe estar en src/)
RUN pip install --no-cache-dir -r requirements.txt

# Define el handler (apunta a tu lambda_handler.py)
CMD ["lambda_handler.handler"]