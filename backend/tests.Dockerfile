FROM python:alpine
COPY ./requirements.txt /src/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt
COPY ./tests /src/tests
COPY ./app /src/app
COPY ./pytest.ini /src/pytest.ini
WORKDIR /src
CMD ["pytest"]
