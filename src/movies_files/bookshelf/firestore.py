{#
# Copyright 2019 Google LLC
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
#}
<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Movie List</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="//maxcdn.bootstrapcdn.com/bootstrap/3.3.2/css/bootstrap.min.css">
  </head>
  <body>
    <div class="navbar navbar-default">
      <div class="container">
        <div class="navbar-header">
          <div class="navbar-brand">Home</div>
        </div>
        <ul class="nav navbar-nav">
          <li><a href="/">Movies</a></li>
        </ul>
        
      </div>
    </div>
    <div class="container">
        <form action="/search_movie" method="post">
                Search for a Movie title: <input type="text" name="movie_id"> 
                <input type="submit" name= "form" value="Search" />
            </form>
        <form action="/filter_genre" method="post">
            or browse by Genre: <input type="text" name="movie_genre"> 
            <input type="submit" name= "form" value="Search" />
        </form>
      {% block content %}{% endblock %}
    </div>
    {{user}}
  </body>
</html>
