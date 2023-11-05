import json

import requests
from botbuilder.core import ActivityHandler, TurnContext, MessageFactory
from botbuilder.schema import ChannelAccount


class QABot(ActivityHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.endpoint = "https://binhna1.cognitiveservices.azure.com/language/:query-knowledgebases"
        self.project_name = "binha-qamaker"
        self.api_version = "2021-10-01"
        self.deployment_name = "production"
        self.subscription_key = "58a071b0c7d54754833adda2f9ce7ec7"
        self.headers = {
            "Ocp-Apim-Subscription-Key": self.subscription_key,
            "Content-Type": "application/json"
        }

    async def on_members_added_activity(
            self, members_added: [ChannelAccount], turn_context: TurnContext
    ):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Hello and welcome! I'm the QA bot")

    def get_answer(self, question, score_threshold, logical_operation):
        data = {
            "top": 3,
            "question": question,
            "includeUnstructuredSources": True,
            "confidenceScoreThreshold": score_threshold,
            "answerSpanRequest": {
                "enable": True,
                "topAnswersWithSpan": 1,
                "confidenceScoreThreshold": score_threshold
            },
            "filters": {
                "metadataFilter": {
                    "logicalOperation": logical_operation,

                }
            }
        }

        response = requests.post(
            f"{self.endpoint}?projectName={self.project_name}&api-version={self.api_version}&deploymentName={self.deployment_name}",
            headers=self.headers,
            data=json.dumps(data)
        )

        return response.json()  # or handle the response as needed

    async def on_message_activity(self, turn_context: TurnContext):

        question = turn_context.activity.text
        response = self.get_answer(question, 0.8, "AND")
        answer = response["answers"][0]["answer"]
        return await turn_context.send_activity(
            MessageFactory.text(f"Answer: {answer}")
        )


if __name__ == '__main__':
    qabot = QABot()
    print(qabot.get_answer("I don’t have insurance. Can I still be seen?", 0.0, "AND"))