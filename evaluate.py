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


# Evaluation prompt template based on G-Eval
EVALUATION_PROMPT_TEMPLATE = """
You will be given one summary written for an article. Your task is to rate the summary on one metric.
Please make sure you read and understand these instructions very carefully. 
Please keep this document open while reviewing, and refer to it as needed.

Evaluation Criteria:

{criteria}

Evaluation Steps:

{steps}

Example:

Source Text:

{document}

Summary:

{summary}

Evaluation Form (scores ONLY):

- {metric_name}
"""

# Metric 1: Relevance

RELEVANCY_SCORE_CRITERIA = """
Relevance(1-5) - selection of important content from the source. \
The summary should include only important information from the source document. \
Annotators were instructed to penalize summaries which contained redundancies and excess information.
"""

RELEVANCY_SCORE_STEPS = """
1. Read the summary and the source document carefully.
2. Compare the summary to the source document and identify the main points of the article.
3. Assess how well the summary covers the main points of the article, and how much irrelevant or redundant information it contains.
4. Assign a relevance score from 1 to 5.
"""

# Metric 2: Coherence

COHERENCE_SCORE_CRITERIA = """
Coherence(1-5) - the collective quality of all sentences. \
We align this dimension with the DUC quality question of structure and coherence \
whereby "the summary should be well-structured and well-organized. \
The summary should not just be a heap of related information, but should build from sentence to a\
coherent body of information about a topic."
"""

COHERENCE_SCORE_STEPS = """
1. Read the article carefully and identify the main topic and key points.
2. Read the summary and compare it to the article. Check if the summary covers the main topic and key points of the article,
and if it presents them in a clear and logical order.
3. Assign a score for coherence on a scale of 1 to 5, where 1 is the lowest and 5 is the highest based on the Evaluation Criteria.
"""

# Metric 3: Consistency

CONSISTENCY_SCORE_CRITERIA = """
Consistency(1-5) - the factual alignment between the summary and the summarized source. \
A factually consistent summary contains only statements that are entailed by the source document. \
Annotators were also asked to penalize summaries that contained hallucinated facts.
"""

CONSISTENCY_SCORE_STEPS = """
1. Read the article carefully and identify the main facts and details it presents.
2. Read the summary and compare it to the article. Check if the summary contains any factual errors that are not supported by the article.
3. Assign a score for consistency based on the Evaluation Criteria.
"""

# Metric 4: Fluency

FLUENCY_SCORE_CRITERIA = """
Fluency(1-3): the quality of the summary in terms of grammar, spelling, punctuation, word choice, and sentence structure.
1: Poor. The summary has many errors that make it hard to understand or sound unnatural.
2: Fair. The summary has some errors that affect the clarity or smoothness of the text, but the main points are still comprehensible.
3: Good. The summary has few or no errors and is easy to read and follow.
"""

FLUENCY_SCORE_STEPS = """
Read the summary and evaluate its fluency based on the given criteria. Assign a fluency score from 1 to 3.
"""


def get_geval_score(
    criteria: str, steps: str, document: str, summary: str, metric_name: str
):
    prompt = EVALUATION_PROMPT_TEMPLATE.format(
        criteria=criteria,
        steps=steps,
        metric_name=metric_name,
        document=document,
        summary=summary,
    )
    response = openai.ChatCompletion.create(
        engine=openai_deployment_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=5,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )

    return response.choices[0].message.content

evaluation_metrics = {
    "Relevance": (RELEVANCY_SCORE_CRITERIA, RELEVANCY_SCORE_STEPS),
    "Coherence": (COHERENCE_SCORE_CRITERIA, COHERENCE_SCORE_STEPS),
    "Consistency": (CONSISTENCY_SCORE_CRITERIA, CONSISTENCY_SCORE_STEPS),
    "Fluency": (FLUENCY_SCORE_CRITERIA, FLUENCY_SCORE_STEPS),
}

def evaluate_summary_openai(document, summary):
    data = {"Evaluation Type": [], "Score": []}
    input_content = document
    response_content = summary.content
    encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')
    input_encode = encoding.encode(input_content)
    response_content_encode = encoding.encode(response_content)
    if len(input_encode) + len(response_content_encode) > 14000:
        input_encode = input_encode[:14000-len(response_content_encode)]
        input_content = encoding.decode(input_encode)
    for eval_type, (criteria, steps) in evaluation_metrics.items():
        data["Evaluation Type"].append(eval_type)
        result = get_geval_score(criteria, steps, input_content, response_content, eval_type)
        score_num = result.strip()
        data["Score"].append(score_num)
    return data