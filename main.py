# Copyright 2020 Google Inc. All Rights Reserved.
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

import os
import logging
from collections import defaultdict

from flask import Flask, request

logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))
logger = logging.getLogger(__name__)

app = Flask(__name__)
moves = ["F", "T", "L", "R"]


class GameLogic:
    # kind of ugly global state ...
    __instance = None

    def __init__(self, data):
        self.update(data)

    def update(self, data):
        self.self_link = data["_links"]["self"]
        self.self_data = data["arena"]["state"][self.self_link]
        self.x = self.self_data["x"]
        self.y = self.self_data["y"]
        self.w = data["arena"]["w"]
        self.h = data["arena"]["h"]
        self.direction = self.self_data["direction"]
        self.pos2obj = defaultdict(lambda: None)
        for obj in data["arena"]:
            self.pos2obj[obj["x"], obj["y"]] = obj

    @classmethod
    def instance(cls, data):
        if not cls.instance:
            cls.instance = cls(data)
        return cls.instance

    def get_colliding_object(self, data):
        x, y = self.x, self.y
        vector = {"N": (0, -1),
                  "S": (0, 1),
                  "E": (1, 0),
                  "W": (-1, 0)}[self.direction]

        for dist in range(max(self.w, self.h)):
            dx, dy = vector
            x += dx
            y += dy
            if o := self.pos2obj[x, y]:
                return o, dist + 1

    def calc_next_move(self, data):
        """first - naive algorithm... go right and throw ball when see someone
        in distance < 10 which is in E or W direction"""
        self.update(data)

        obj, distance = self.get_colliding_object(data)
        if obj["direction"] in ["W", "E"] and distance < 10:
            logger.info(f"found {obj} in distance {distance}, throwing ball")
            return "T"

        if self.direction == "E":
            logger.info("forward! to the east, there must be live there")
            return "F"

        if self.direction in ["W", "N"]:
            logger.info(f"Im directed to {self.direction} - turn right")
            return "R"

        if self.direction == "S":
            logger.info(f"Im directed to {self.direction} - turn left")
            return "L"


@app.route("/", methods=["GET"])
def index():
    return "Let the battle begin!"


@app.route("/", methods=["POST"])
def move():
    data = request.get_data()
    logger.info(request.json)
    return GameLogic.instance(data).calc_next_move(data)


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0",
            port=int(os.environ.get("PORT", 8080)))
