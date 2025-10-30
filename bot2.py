from dotenv import load_dotenv
from typing import TypedDict , Optional , List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from langgraph.graph import  START , END , StateGraph
from pydantic_core.core_schema import model_field

load_dotenv()


model = ChatGoogleGenerativeAI(model="gemini-2.5-flash" , temperature=2)


class Sat_State(TypedDict):
    Subject:  str
    Topic : str
    Difficulty : str
    Instructions : Optional[str]
    Questions : Optional[str]
    History : Optional[List[str]]

class Output_format(BaseModel):
    question: str = Field(description="only contains The SAT question text without Options and answer.")
    option_a: str = Field(description="Option A text")
    option_b: str = Field(description="Option B text")
    option_c: str = Field(description="Option C text")
    option_d: str = Field(description="Option D text")
    correct_answer: str = Field(description="Correct answer letter (A, B, C, or D)")
    explanation: str = Field(description="Brief explanation of the correct answer")

parser = JsonOutputParser(pydantic_object=Output_format)

def genrater_que(state: Sat_State) -> Sat_State:
    prompt = PromptTemplate(
        template="""
        You are an expert SAT tutor.
        Your task is to create some SAT Questions that can help student to get high score in real SAT exam.
        you will be given Subject , topic , difficulty level and some instructions if nedded.
        You will create only 1 question based on the given information.
        Each question should have 4 options and only one correct answer.
        You will also provide the correct answer for each question.
        every time question should be different.
        Do not repeat same question multiple times.
        Subject: {Subject}
        Topic: {Topic}
        Difficulty: {Difficulty}
        Additional Instructions: {Instructions}
        previous Generated Questions: {History}
        Return output with Streamlit latext support if subject is maths
        Return your answer strictly as JSON in this formate:
        {format_instructions}""",
         input_variables=["Subject", "Topic", "Difficulty", "Instructions","History"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )



    chain = prompt | model | parser
    genrated_question = chain.invoke({
        "Subject" : state["Subject"],
        "Topic" : state["Topic"],
        "Difficulty" : state["Difficulty"],
        "Instructions" : state["Instructions"] if state["Instructions"] else "No additional instructions",
        "History" : state["History"] if state["History"] else "No Previous question"

    })



    state["Questions"] = genrated_question
    return state


graph = StateGraph(Sat_State)
graph.add_node("Genrater_Questions",genrater_que)

graph.add_edge(START,"Genrater_Questions")
graph.add_edge("Genrater_Questions",END)

bot = graph.compile()

# print(f"bot" , bot.invoke(initial_Sat_State)['Questions'].content)

