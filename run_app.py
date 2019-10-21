from rasa_core.channels import HttpInputChannel
from rasa_core.agent import Agent
from rasa_core.interpreter import RasaNLUInterpreter
from rasa_slack_connector import SlackInput


nlu_interpreter = RasaNLUInterpreter('./models/nlu/default/restaurantnlu')
agent = Agent.load('./models/dialogue', interpreter = nlu_interpreter)

input_channel = SlackInput('xoxp-793700993141-795904281718-801935304960-193229b9936ba8dd646894ce29dae032', #app verification token
							'xoxb-793700993141-801471113892-QwRTM7rn36zeqeNWzcCyHv9D', # bot verification token
							'AuVGI6Eaw6pL9NMzZ36qWAsU', # slack verification token
							True)

agent.handle_channel(HttpInputChannel(5004, '/', input_channel))