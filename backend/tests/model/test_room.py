import pytest
from app.model.room import RoomModel

# @pytest.fixture
# def client():
#     yield app

class TestRoomModel:

    def test_diffsHandler_PASS(self):
        room = RoomModel("test_code")
        assert room.__diffsHandler__(["1", "2", "3"], {0: "hello", 3: "2"}) == ["hello", "2", "3", "2"]
        assert room.__diffsHandler__(["1", "2", "3"], {0: "hello", 5: "2"}) == ["hello", "2", "3", "", "", "2"]
        assert room.__diffsHandler__(["1", "2", "3"], {0: "hello", 2: None}) == ["hello", "2"]

        with pytest.raises(ValueError):
            room.__diffsHandler__(["1", "2", "3"], {0: None, 5: None})
        with pytest.raises(ValueError):
            print(room.__diffsHandler__(["1", "2", "3"], {8: None}))
            room.__diffsHandler__(["1", "2", "3"], {8: None}) 
        with pytest.raises(ValueError):
            room.__diffsHandler__(["1", "2", "3", "4", "5"], {2: None}) 
    
    def test_setRun(self):
        room = RoomModel("test_code")

        room.code = ["print(\"hello world\")"]
        stdout, stderr = room.run()
        assert stdout == ["hello world"] 
        assert stderr == [] 

        room.stdin = ["10"]
        room.code = ["print(int(input()) + 10)"]
        stdout, stderr = room.run()
        assert stdout == ["20"] 
        assert stderr == [] 

        room.code = ["dfkjdsfhsdf"]
        stdout, stderr = room.run()
        assert stdout == [] 
        assert stderr != [] 