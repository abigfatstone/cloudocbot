# Basd on Deep Q&A

## Installation

The program requires the following dependencies (easy to install using pip):
 * python 3.5
 * tensorflow (tested with v1.0)
 * numpy
 * CUDA (for using GPU)
 * nltk (natural language toolkit for tokenized the sentences)
 * tqdm (for the nice progression bars)

You might also need to download additional data to make nltk work.

```
python3 -m nltk.downloader punkt
```

The Cornell dataset is already included. For the other datasets, look at the readme files into their respective folders (inside `data/`).

The web interface requires some additional packages:
 * django (tested with 1.10)
 * channels
 * Redis (see [here](http://redis.io/topics/quickstart))
 * asgi_redis (at least 1.0)

### Web interface

Once trained, it's possible to chat with it using a more user friendly interface. The server will look at the model present on `save/model-server/model.ckpt`. The first time you want to use it, you'll need to configure it with:

```bash
export CHATBOT_SECRET_KEY="my-secret-key"
cd chatbot_website/
python3 manage.py makemigrations
python3 manage.py migrate
```

Then, to launch the server locally, use the following commands:

```bash
cd chatbot_website/
redis-server &  # Launch Redis in background
nohup /workHome/python3/bin/python3 /cloudocBot/chatbot_website/manage.py runserver 0.0.0.0:8000 &
```

After launch, the interface should be available on [http://localhost:8000/](http://localhost:8000/). If you want to deploy the program on a server, use `python manage.py runserver 0.0.0.0` instead. More info [here](https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/).

# cloudocbot
