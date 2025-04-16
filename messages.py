import prelogic
import typing

common = prelogic.common

def check_udp_message_validation(jsondata: dict[str, typing.Any], addr: tuple[str,str]) -> bool:
    if ("type" in jsondata 
        and isinstance(jsondata["type"], str)):
        try:
            add = jsondata["add"]
            if add["game"] != common.version.GAME:
                common.LOG(addr[0] + ": " + f"Different games - {common.version.GAME} and {add["game"]}")
                return False
            
            if add["version"] != common.version.VERSION:
                common.LOG(addr[0] + ": " + f"Different versions - {common.version.VERSION} and {add["version"]}")
                return False
            username = add["name"]
            username = username[0:16]
            if not isinstance(username, str):
                common.LOG(addr[0] + ": " + f"Invalid name")
                return False
            
            return True
        except Exception:
            # print(e)
            common.LOG(addr[0] + ": " + "Invalid json file structure")
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