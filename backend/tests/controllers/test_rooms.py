from flask import request
from app.main import app
import pytest
from app.controllers.rooms import RoomController
from app.model.room import RoomModel

# @pytest.fixture
# def client():
#     yield app

class TestRoomController:
    def test_formatListToJson_PASS(self):
        with app.test_request_context("/?room_code=test_code"):
            rooms = dict({"test_code": RoomModel("test_code")})
            request.sid = "test_sid"
            request.cookies = dict({"auth": "test_auth"})
            room_c = RoomController(request, rooms)
            assert room_c.__formatListToJson__(["1", "2", "3"]) == dict({0: "1", 1:"2", 2:"3"})

    def test_formatListToJson_FAIL(self):
        with app.test_request_context("/?room_code=test_code"):
            rooms = dict({"test_code": RoomModel("test_code")})
            request.sid = "test_sid"
            request.cookies = dict({"auth": "test_auth"})
            room_c = RoomController(request, rooms)
            with pytest.raises(TypeError):
                room_c.__formatListToJson__(dict({0: "1", 1:"2", 2:"3"})) 
