from typing import Sequence, TypedDict, List, Union, Annotated
from dotenv import load_dotenv  
from langchain_core.messages import BaseMessage
from langchain_core.messages import ToolMessage
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from datetime import datetime

import asyncio
from kuksa_client.grpc.aio import VSSClient
from kuksa_client.grpc import Datapoint

import pygame
from gtts import gTTS
import os
import time

import json

load_dotenv()

import sqlite3

try:
    connection = sqlite3.connect("history.db")
    cursor = connection.cursor()
    print("✅ Your database is ready. ")
except:
    print("❌ Something is wrong, can't open database. ")

try:
    get_date = datetime.now().strftime("%Y_%m_%d")
    table_name = f"'{get_date}_table'"
    check_table = cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name={table_name}")
    if check_table.fetchone():
        print("✅ Table exit")
    else:
        cursor.execute(f"""
                            CREATE TABLE {table_name} (
                                human_messages str,
                                ai_messages int
                            )
                        """)
        connection.commit()
        print("✅ Successfull created table")
except Exception as e:
    print("Facing error when try to creating or connecting to table: ", e)

try:
    with open('define.json') as F:
        configure = json.load(F)
except Exception as e:
    print("Error: " , e)

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

vss = VSSClient(configure["ip_address"], configure["port"])

async def main():
    async with vss as client:
        current_values = await client.get_current_values([
            'Vehicle.Speed',
        ])
        if current_values['Vehicle.Speed'] is not None:
            speed = f"{current_values['Vehicle.Speed'].value} km/h"
        else:
            speed = f"0 km.h"

    return speed

async def set_speed(new_speed: float):
    try:
        async with vss as client:
            # Assuming your client has a method to set values 
            success = await client.set_current_values({
            "Vehicle.Speed": Datapoint(new_speed)
        })
            return success
    except Exception as e:
        # handle or log error
        return False
    
async def seat_state():
    async with vss as client:
        current_values = await client.get_target_values([
            'Vehicle.Cabin.Seat.Row1.DriverSide.Position',
        ])
        if current_values['Vehicle.Cabin.Seat.Row1.DriverSide.Position'] is not None:
            speed = f"{current_values['Vehicle.Cabin.Seat.Row1.DriverSide.Position'].value} level"
        else:
            speed = f"0 level"

    return speed

async def set_seat(new_level: float):
    try:
        async with vss as client:
            # Assuming your client has a method to set values 
            success = await client.set_target_values({
            "Vehicle.Cabin.Seat.Row1.DriverSide.Position": Datapoint(new_level)
        })
            return success
    except Exception as e:
        # handle or log error
        return False

async def lights_state(type):
    async with vss as client:
        low_beam = await client.get_target_values([
            f"{type}"
        ])
        if low_beam[f"{type}"].value :
            state = "On"
        else:
            state = "Off"
    return state

async def set_lights(new_state: bool, type: str):
    try:
        async with vss as client:
            success = await client.set_target_values({
                f"{type}": Datapoint(new_state)
            })
            return success
    except:
        return False
    
async def set_fan(new_state: bool, type: str):
    try:
        async with vss as client:
            success = await client.set_target_values({
                f"{type}": Datapoint(new_state)
            })
            return success
    except:
        return False
    
async def fan_state(type):
    async with vss as client:
        low_beam = await client.get_target_values([
            f"{type}"
        ])
        if low_beam[f"{type}"].value > 0:
            state = f"Fan On and running at {low_beam[type].value}"
        else:
            state = "Off"
    return state

@tool
def fan_teller(fan_type: str):
    """Tool to check what kind of fan the user want to check. there are 2 types of api for you to choose.
        the frist api is for Passenger Fan speed : "Vehicle.Cabin.HVAC.Station.Row1.Passenger.FanSpeed".
        the second api is for Driver Fan Speed : "Vehicle.Cabin.HVAC.Station.Row1.Driver.FanSpeed".
        Choose the api based on the user demand
        Args:
            fan_type (str): Pass the api based on fan type the user want.
    """
    state = asyncio.run(fan_state(fan_type))
    
    return state

@tool
def light_teller(lights_type: str):
    """ Tool to check what kind of lights the user want to check. there are 3 types of api for you to choose.
        the frist api is for low beam lights : "Vehicle.Body.Lights.Beam.Low.IsOn".
        the second api is for high beam lights : "Vehicle.Body.Lights.Beam.High.IsOn".
        the third api is for hazard lights: "Vehicle.Body.Lights.Hazard.IsSignaling".
        Choose the api based on the user demand
        Args:
            lights_type (str): The api based on what user say.
    """

    state = asyncio.run(lights_state(lights_type))
    return state

@tool
def speed_setter(speed: float):
    """
    Tool to set the vehicle speed.
    Args:
        speed (float): The speed to set the vehicle to.
    Returns:
        bool: True if speed was set successfully, False otherwise.
    """
    result = asyncio.run(set_speed(speed))
    return result

@tool
def light_setter(state: bool, light_type: str):
    """
        Tool to set the vehicle lights.
        Tool to check what kind of lights the user want to check. there are 3 types of api for you to choose.
        the frist api is for low beam lights : "Vehicle.Body.Lights.Beam.Low.IsOn".
        the second api is for high beam lights : "Vehicle.Body.Lights.Beam.High.IsOn".
        the third api is for head lights or hazard lights: "Vehicle.Body.Lights.Hazard.IsSignaling".
        Choose the api based on the user demand
        Args:
            lights_type (str): The api based on what user say.
            state (bool): The state of the low beam lights to set the vehicle to
        Returns:
            bool: True if lights was set succesffully, False otherwise
    """
    result = asyncio.run(set_lights(state, light_type))
    return result

@tool
def fan_setter(fan_type: str, state: int):
    """Tool to check what kind of fan the user want to check. there are 2 types of api for you to choose.
        the frist api is for Passenger Fan speed : "Vehicle.Cabin.HVAC.Station.Row1.Passenger.FanSpeed".
        the second api is for Driver Fan Speed : "Vehicle.Cabin.HVAC.Station.Row1.Driver.FanSpeed".
        Choose the api based on the user demand
        Args:
            fan_type (str): The api based on what user say.
            state (bool): The percentage of power , user want to set fan to 
        Returns:
            bool: True if lights was set succesffully, False otherwise
    """
    result = asyncio.run(set_fan(state, fan_type))
    return result
@tool
def seat_setter(level: float):
    """
    Tool to set the vehicle seat posistion.
    Args:
        level (float): The user seat possition.
    Returns:
        bool: True if speed was set successfully, False otherwise.
    """
    result = asyncio.run(set_seat(level))
    return result

@tool
def seat_teller(seat: str):
    """ seat teller function """
    seat = asyncio.run(seat_state())
    return seat

@tool
def speed_teller(speed: str):
    """ speed teller function """
    speed = asyncio.run(main())
    return speed

@tool
def time_teller():
    """Returns the current time."""
    return datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")

tools = [time_teller, speed_teller, speed_setter, light_teller, light_setter,fan_teller, fan_setter, seat_teller, seat_setter]

try:
    model = ChatOllama(model = configure['tool_model']).bind_tools(tools)
    llm = ChatOllama(model = configure['com_model'])
    print("AI model is ready")
except:
    print("There is something wrong with AI model")

language='en'
accent='co.uk'
tem_mp3="temp_audio.mp3"

def speech(speak_data):
    speech = gTTS(lang=language , text= f"{speak_data }", tld= accent, slow=False)
    pygame.mixer.init()
    speech.save(tem_mp3)
    pygame.mixer.music.load(tem_mp3)
    pygame.mixer.music.play()
    
    while pygame.mixer.music.get_busy():
        time.sleep(0.5)
    # os.remove(tem_mp3)

#async def async_print(content):
#    await asyncio.to_thread(print, content, end="", flush=True)

def model_call(state: AgentState) -> AgentState:
    system_prompt = SystemMessage(content="""
        There are couple of information you can check and change in this car such as speed , lights , fan speed and set posstion.
        The first one is speed : detect if user asking for somelike 'tell me the speed' or 'how fast we are going', that mean user want to know the speed right now. Therefore, call tool 'speed_teller'. 
            If the user saying something like 'set up speed to ' or 'change speed to ', that means they want to change the car speed, call 'speed_setter' tool to change speed.
        The second one is lights, there are 3 kind of lights low beam lights, high beam lights and hazard lights. 
            (Note: user can prefer to those with different name such as 'low beam' or 'low lights' for low beam lights, 
                                                                        'high beam' or 'high lights' for high beam lights
                                                                        'head lights' or 'hazard' for hazard lights,
                                                                        if user say 'all lights' that mean user prefer to every kind of lights you have)
            If the user saying something like ' state of lights' or 'tell me if lights is on', that mean the user want to know the state of lights, call the 'light_teller' to detect what kind of lights, and the state of that lights the user is perfering to.
            However, If the user is asking for something like 'turn lights on ', 'turn lights off', 'set lights on ' or 'set lights off', that mean user want to change the state of lights, if so call 'light_setter' tool, then detect what kind of lights, user want to change state and the state of lights user want to set up to
        The third thing is fan speed, there are 2 kind of fan speed you have access to the first is driver fan speed and the other one is passenger fan speed.
            If the user saying somethinkg like 'state of fan speed ' or 'tell me how fast is fan speed', that likely mean user want to know the speed fan is moving right now, call the 'fan_teller' tool, then detect the kind of fan user prefering to and tell user that fan speed state.
            If the user asking for something like 'set fan speed to ' or 'change fan speed to', that mean user want to edit the speed of the fan, call 'fan_setter' then detect what kind of fan speed the user is prefering to and set that fan to the speed user want to.
        The fourth want is user seat possition, the user seat have couple of levels, ranging from 0 to 10.
            if the user asking you something like 'state of seat' or 'telling me the seat possition' then user want you to tell them the state of seat at the moment, call 'seat_teller' and tell the user seat possition at the momment.
            If user saying something like ' set seat possition to' or 'change seat possition to ', user likely want you to edit the seat possition, call 'seat_setter' to detect the value then pass the value user said in.  
        If the user asking anything about the 'time' including 'month', 'day', 'minnute', 'hour',... then call tool 'time_teller'
    """)

    last_user_input = ""
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            last_user_input = msg.content.lower()
            break

    allowed_keywords = ["time", "clock", "date", "today", "speed", "fast", "lights", "low beam", "low", "high", "beam", "hazard","turn", "on","off", "fan", "seat", "position"]

    is_tool_needed = any(keyword in last_user_input for keyword in allowed_keywords)

    if is_tool_needed:
        
        response = model.invoke([configure["name"]] + [configure["definition"]] + [system_prompt] + state["messages"])
        print("Thinking...")

        if hasattr(response, "tool_calls") and response.tool_calls:
            print("\nAI is making a tool call")
            for call in response.tool_calls:
                print(f"→ Tool: {call['name']}, Arguments: {call['args']}")
        else:
            speech(response.content)
            print("\nAI: ", response.content)

        state["messages"].append(response)
        return state
    else:
        response = llm.stream([configure["name"]] + [configure["definition"]] + [system_prompt] + state["messages"])
        full_response = ""
        print("Thinking... ")
        frist_res = False

        if response:
            for res in response:
                if not frist_res:
                    frist_res = True
                    print("\nAI: ", end="" , flush= True)
                print(res.content, end="", flush=True)
                full_response += res.content
            try:
                check_json = json.loads(full_response)
                state["messages"].append(AIMessage(content= "Failed"))
            except (ValueError, TypeError):
                speech(full_response)
                state["messages"].append(AIMessage(content= full_response))
        else:
            print("\nAI: [No meaningful response generated]")

        return state


def should_continue(state: AgentState): 
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls: 
        return "tools"
    else:
        return "end"
    
graph = StateGraph(AgentState)
graph.add_edge("tools", "our_agent")
graph.add_node("our_agent", model_call)

tool_node = ToolNode(tools=tools)
graph.add_node("tools", tool_node)

graph.set_entry_point("our_agent")

graph.add_conditional_edges(
    "our_agent",
    should_continue,
    {
        "tools": "tools",
        "end": END,
    },
)

graph.add_edge(START, "our_agent")
graph.add_edge("our_agent", END)

agent = graph.compile()

history = []

agent.invoke({"messages": [HumanMessage(content= "Hello")]})

while True:
    user_input = input("\nEnter: ")

    if user_input in ["end", "exit", "clode", "goodbye"]:
        print("Turning model off...")
        break
    history.append(HumanMessage(content= user_input))
    result = agent.invoke({"messages" : history})
    try:
        if len(history) > 0:
            ai_mess = history[-1].content
            cursor.execute(f"INSERT INTO {table_name} VALUES (?,?)", (user_input, ai_mess))
            connection.commit()
    except Exception as e:
        print("Failed to store conversation: ", e)
    history = result["messages"]
connection.close()
print(f"\n✅ Successfull turn model {configure['tool_model']} and {configure['com_model']}")