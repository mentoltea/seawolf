import typing

import prelogic
from prelogic import common
from common import json
# common = prelogic.common

def check_udp_message_validation(jsondata: dict[str, typing.Any], addr: tuple[str,str]) -> bool:
    if ("type" in jsondata 
        and isinstance(jsondata["type"], str)):
        try:
            add = jsondata["add"]
            if add["game"] != common.version.GAME:
                prelogic.LOG(addr[0] + ": " + f'Different games - {common.version.GAME} and {add["game"]}')
                return False
            
            if add["version"] != common.version.VERSION:
                prelogic.LOG(addr[0] + ": " + f'Different versions - {common.version.VERSION} and {add["version"]}')
                return False
            username = add["name"]
            username = username[0:16]
            if not isinstance(username, str):
                prelogic.LOG(addr[0] + ": " + f"Invalid name")
                return False
            
            return True
        except Exception:
            # print(e)
            prelogic.LOG(addr[0] + ": " + "Invalid json file structure")
            # print(jsondata)
    return False


def broadcast_message() -> str:
    return common.json.dumps(
        {
            "type" : f"{common.MessageType.BROADCAST}",
            "add" : {
                "game" : f"{common.version.GAME}",
                "version" : f"{common.version.VERSION}",
                "name" : f"{prelogic.MYUSERNAME}"
            }
        }
    )

def request_connection_message() -> str:
    return common.json.dumps(
        {
            "type" : f"{common.MessageType.REQUEST_CONN}",
            "add" : {
                "game" : f"{common.version.GAME}",
                "version" : f"{common.version.VERSION}",
                "name" : f"{prelogic.MYUSERNAME}"
            }
        }
    )

def accept_connection_message(port: int = prelogic.connection.TCP_PORT) -> str:
    return common.json.dumps(
        {
            "type" : f"{common.MessageType.ANSWER_CONN}",
            "add" : {
                "game" : f"{common.version.GAME}",
                "version" : f"{common.version.VERSION}",
                "name" : f"{prelogic.MYUSERNAME}"
            },
            "connection" : {
                "status" : True,
                "port" : f"{port}"
            }
        }
    )

def reject_connection_message(port:int = prelogic.connection.TCP_PORT) -> str:
    return common.json.dumps(
        {
            "type" : f"{common.MessageType.ANSWER_CONN}",
            "add" : {
                "game" : f"{common.version.GAME}",
                "version" : f"{common.version.VERSION}",
                "name" : f"{prelogic.MYUSERNAME}"
            },
            "connection" : {
                "status" : False
            }
        }
    )

# <- UDP
# -------------------------------
#    TCP ->

TCP_DELIMITER = ";"

def check_conn_message() -> str:
    return common.json.dumps(
        {
            "type" : f"{common.MessageType.CHECK_CONN}",
        }
    ) + TCP_DELIMITER

def ready_message() -> str:
    return common.json.dumps(
        {
            "type" : f"{common.MessageType.GAME_EVENT}",
            "event" : {
                "type" : f"{common.GameEventType.READY}"
            }
        }
    ) + TCP_DELIMITER
    
def unready_message() -> str:
    return common.json.dumps(
        {
            "type" : f"{common.MessageType.GAME_EVENT}",
            "event" : {
                "type" : f"{common.GameEventType.UNREADY}"
            }
        }
    ) + TCP_DELIMITER

def ask_start_game_message() -> str:
    return common.json.dumps(
        {
            "type" : f"{common.MessageType.GAME_EVENT}",
            "event" : {
                "type" : f"{common.GameEventType.ASK_START_GAME}"
            }
        }
    ) + TCP_DELIMITER

def start_game_decl_message() -> str:
    return common.json.dumps(
        {
            "type" : f"{common.MessageType.GAME_EVENT}",
            "event" : {
                "type" : f"{common.GameEventType.START_GAME_DECLINE}"
            }
        }
    ) + TCP_DELIMITER

def start_game_appr_message() -> str:
    return common.json.dumps(
        {
            "type" : f"{common.MessageType.GAME_EVENT}",
            "event" : {
                "type" : f"{common.GameEventType.START_GAME_APPROVE}"
            }
        }
    ) + TCP_DELIMITER
    
def start_game_sappr_message() -> str:
    return common.json.dumps(
        {
            "type" : f"{common.MessageType.GAME_EVENT}",
            "event" : {
                "type" : f"{common.GameEventType.START_GAME_SECOND_APPROVE}"
            }
        }
    ) + TCP_DELIMITER

def surrender_game_message() -> str:
    return common.json.dumps(
        {
            "type" : f"{common.MessageType.GAME_EVENT}",
            "event" : {
                "type" : f"{common.GameEventType.SURRENDER_GAME}"
            }
        }
    ) + TCP_DELIMITER


def end_game_message() -> str:
    return common.json.dumps(
        {
            "type" : f"{common.MessageType.GAME_EVENT}",
            "event" : {
                "type" : f"{common.GameEventType.END_GAME}"
            }
        }
    ) + TCP_DELIMITER

def make_move_message(move: str) -> str:
    return common.json.dumps(
        {
            "type" : f"{common.MessageType.GAME_EVENT}",
            "event" : {
                "type" : f"{common.GameEventType.MAKE_MOVE}",
                "move" : f"{move}"
            }
        }
    ) + TCP_DELIMITER

def move_empty_message(move: str) -> str:
    return common.json.dumps(
        {
            "type" : f"{common.MessageType.GAME_EVENT}",
            "event" : {
                "type" : f"{common.GameEventType.MOVE_EMPTY}",
                "move" : f"{move}"
            }
        }
    ) + TCP_DELIMITER
    
def move_shot_message(move: str) -> str:
    return common.json.dumps(
        {
            "type" : f"{common.MessageType.GAME_EVENT}",
            "event" : {
                "type" : f"{common.GameEventType.MOVE_SHOT}",
                "move" : f"{move}"
            }
        }
    ) + TCP_DELIMITER
    
def move_killed_message(move: str) -> str:
    return common.json.dumps(
        {
            "type" : f"{common.MessageType.GAME_EVENT}",
            "event" : {
                "type" : f"{common.GameEventType.MOVE_KILLED}",
                "move" : f"{move}"
            }
        }
    ) + TCP_DELIMITER
    
def bad_move_message(move: str) -> str:
    return common.json.dumps(
        {
            "type" : f"{common.MessageType.GAME_EVENT}",
            "event" : {
                "type" : f"{common.GameEventType.BAD_MOVE}",
                "move" : f"{move}"
            }
        }
    ) + TCP_DELIMITER







# --------------------------------
# Abandoned ->

def message_is_check_conn(data: str | bytes | None) -> bool:
    if data == None:
        return False
    try:
        jsondata = json.loads(data)
        _type: str = jsondata["type"]
        if _type == common.MessageType.CHECK_CONN:
            return True
        return False
    except Exception as e:
        print(str(e))
        return False

def check_conn_message_check(data: str | bytes | None) -> bool:
    if data == None:
        return False
    try:
        jsondata = json.loads(data)
        _type: str = jsondata["type"]
        if _type == common.MessageType.CHECK_CONN:
            return True
        prelogic.LOG("Unsupported type")
        return False
    except Exception as e:
        prelogic.ERROR(str(e))
        prelogic.LOG("Invalid json file structure")
        return False

def approve_conn_message() -> str:
    return common.json.dumps(
        {
            "type" : f"{common.MessageType.APPROVE_CONN}",
        }
    )

def approve_conn_message_check(data: str | bytes | None) -> bool:
    if data == None:
        return False
    try:
        jsondata = json.loads(data)
        _type: str = jsondata["type"]
        if _type == common.MessageType.APPROVE_CONN:
            return True
        prelogic.LOG("Unsupported type")
        return False
    except Exception as e:
        prelogic.ERROR(str(e))
        prelogic.LOG("Invalid json file structure")
        return False