# Copyright 2015 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from moviesshelf import get_model, storage
from flask import current_app
from google.cloud import pubsub
import psq
import requests


publisher_client = pubsub.PublisherClient()
subscriber_client = pubsub.SubscriberClient()


def get_moviess_queue():
    project = current_app.config['PROJECT_ID']

    # Create a queue specifically for processing moviess and pass in the
    # Flask application context. This ensures that tasks will have access
    # to any extensions / configuration specified to the app, such as
    # models.
    return psq.Queue(
        publisher_client, subscriber_client, project,
        'moviess', extra_context=current_app.app_context)


def process_movies(movies_id):
    """
    Handles an individual moviesshelf message by looking it up in the
    model, querying the Google moviess API, and updating the movies in the model
    with the info found in the moviess API.
    """

    model = get_model()

    movies = model.read(movies_id)

    if not movies:
        logging.warn("Could not find movies with id {}".format(movies_id))
        return

    if 'title' not in movies:
        logging.warn("Can't process movies id {} without a title."
                     .format(movies_id))
        return

    logging.info("Looking up movies with title {}".format(movies[
                                                        'title']))

    new_movies_data = query_moviess_api(movies['title'])

    if not new_movies_data:
        return

    movies['title'] = new_movies_data.get('title')
    movies['author'] = ', '.join(new_movies_data.get('authors', []))
    movies['publishedDate'] = new_movies_data.get('publishedDate')
    movies['description'] = new_movies_data.get('description')

    # If the new movies data has thumbnail images and there isn't currently a
    # thumbnail for the movies, then copy the image to cloud storage and update
    # the movies data.
    if not movies.get('imageUrl') and 'imageLinks' in new_movies_data:
        new_img_src = new_movies_data['imageLinks']['smallThumbnail']
        movies['imageUrl'] = download_and_upload_image(
            new_img_src,
            "{}.jpg".format(movies['title']))

    model.update(movies, movies_id)


def query_moviess_api(title):
    """
    Queries the Google moviess API to find detailed information about the movies
    with the given title.
    """
    r = requests.get('https://www.googleapis.com/moviess/v1/volumes', params={
        'q': title
    })

    try:
        data = r.json()['items'][0]['volumeInfo']
        return data

    except KeyError:
        logging.info("No movies found for title {}".format(title))
        return None

    except ValueError:
        logging.info("Unexpected response from moviess API: {}".format(r))
        return None


def download_and_upload_image(src, dst_filename):
    """
    Downloads an image file and then uploads it to Google Cloud Storage,
    essentially re-hosting the image in GCS. Returns the public URL of the
    image in GCS
    """
    r = requests.get(src)

    if not r.status_code == 200:
        return

    return storage.upload_file(
        r.content,
        dst_filename,
        r.headers.get('content-type', 'image/jpeg'))
