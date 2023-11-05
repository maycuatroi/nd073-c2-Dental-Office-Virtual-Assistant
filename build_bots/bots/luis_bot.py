from pprint import pprint

import requests
from botbuilder.core import ActivityHandler, TurnContext, MessageFactory
from botbuilder.schema import ChannelAccount


class LUISBot(ActivityHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.endpoint = "https://binhna1.cognitiveservices.azure.com/language/:analyze-conversations"
        self.api_version = "2022-10-01-preview"
        self.subscription_key = "58a071b0c7d54754833adda2f9ce7ec7"
        self.headers = {
            "Ocp-Apim-Subscription-Key": self.subscription_key,
            "Apim-Request-Id": "4ffcac1c-b2fc-48ba-bd6d-b69d9942995a",
            "Content-Type": "application/json"
        }

    async def on_members_added_activity(
            self, members_added: [ChannelAccount], turn_context: TurnContext
    ):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Hello and welcome! I'm the QA bot")

    def analyze_conversation(self, participant_id, query):
        data = {
            "kind": "Conversation",
            "analysisInput": {
                "conversationItem": {
                    "id": participant_id,
                    "text": query,
                    "modality": "text",
                    # "language": language,
                    "participantId": participant_id
                }
            },
            "parameters": {
                "projectName": "binhna-conversation",
                "verbose": True,
                "deploymentName": "binhna-deployment",
                "stringIndexType": "TextElement_V8"
            }
        }

        response = requests.post(
            f"{self.endpoint}?api-version={self.api_version}",
            headers=self.headers,
            json=data
        )

        return response.json()

    async def on_message_activity(self, turn_context: TurnContext):

        question = turn_context.activity.text
        participant_id = turn_context.activity.from_property.id
        response = self.analyze_conversation(participant_id, question)

        intent = response["result"]["prediction"]["topIntent"]
        if intent == "Find appointment schedule":
            avaiable_schedule = self.get_available_schedule()
            avaiable_schedule = ', '.join(avaiable_schedule)
            answer = f"The available schedule is: {avaiable_schedule}"
        else:
            answer = "I don't understand your question"

        return await turn_context.send_activity(
            MessageFactory.text(f"Answer: {answer}")
        )

    def get_available_schedule(self):
        url = 'http://localhost:3000/availability'
        data = requests.get(url).json()
        return data


if __name__ == '__main__':
    qabot = LUISBot()
    pprint(qabot.analyze_conversation('#1', "What appointments are available?"))
