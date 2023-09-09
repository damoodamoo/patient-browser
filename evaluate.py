import os
import openai
import tiktoken
from langchain.evaluation import load_evaluator
from langchain.evaluation import EvaluatorType
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
load_dotenv(f'{os.path.dirname(__file__)}/../../.env')

openai.api_type = "azure"
openai.api_version = "2023-03-15-preview"
openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_key = os.getenv("OPENAI_API_KEY")
openai_deployment_name = os.getenv("OPENAI_DEPLOYMENT_NAME")

custom_criterion = {"numeric": "Does the output present a correct and concise summary of the input?"}

llm = ChatOpenAI(max_tokens=500,
                 engine=openai_deployment_name,
                 openai_api_base=os.getenv("OPENAI_API_BASE"),
                 openai_api_key=os.getenv("OPENAI_API_KEY"),
                 temperature=0,)

evaluator = load_evaluator(
    EvaluatorType.CRITERIA,
    criteria=custom_criterion,
    llm=llm
)

#evaluator = load_evaluator("criteria", criteria="conciseness")

# Write function to evaluate LLM response
def evaluate_summary(input, response):
    input_content = input
    response_content = response.content
    encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')
    input_encode = encoding.encode(input_content)
    response_content_encode = encoding.encode(response_content)
    if len(input_encode) + len(response_content_encode) > 14000:
        input_encode = input_encode[:14000-len(response_content_encode)]
        input_content = encoding.decode(input_encode)
    eval_result = evaluator.evaluate_strings(prediction=response_content, input=input_content)
    return eval_result