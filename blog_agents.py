from crewai import Agent
from crewai_tools import SerperDevTool
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

search_tool = SerperDevTool()


llm=ChatOpenAI(
    temperature=0.2,
    model_name="gpt-4-turbo",
)


class BlogAgents():
    def fintech_expert_agent(self):
        return Agent(
            role="Fintech Expert",
            goal="Research on given topic for fintech audiences",
            verbose=True,
            memory=True,
            backstory=(
                "As a fintech enthusiast, you are dedicated to exploring"
                " the latest trends and technologies in fintech. Your passion for the subject"
                " drives you to delve deep into each topic, providing your readers with insightful"
                " and actionable content."
            ),
            tools=[search_tool],
            max_iter=15,
            llm=llm,
            allow_delegation=True
        )

    def writer_chief_agent(self):
        return Agent(
            role="Chief Writer",
            goal="Write a draft article on the given topic, ensure that "
                 "each sub sections are assigned to exact one senior writer.",
            verbose=True,
            memory=True,
            llm=llm,
            backstory=(
                "An expert on fintech topics, you are dedicated to crafting"
                "With a flair for simplifying complex topics, you craft"
                "engaging narratives that captivate and educate, bringing new"
                "discoveries to light in an accessible manner."
                "Excellent at delegating tasks for sections writing to the senior writers team."
            ),
            max_iter=10,
            tools=[search_tool],
            allow_delegation=True
        )
    def writer_senior_agent(self):
        return Agent(
            role="Senior Writer",
            goal="Write a section on the sub topic assigned by Chief Writer, put original citation links in section.",
            verbose=True,
            memory=True,
            llm=llm,
            backstory=(
                "With a flair for simplifying complex topics, you craft"
                "engaging narratives that captivate and educate, bringing new"
                "discoveries to light in an accessible manner."
                "you are good at adding inline citations to the content to make it more reliable."
            ),
            max_iter=15,
            tools=[search_tool],
            allow_delegation=False
        )




    def editor_agent(self):
        return Agent(
            role="Editor",
            goal="Edit a given blog post to align with "
                 "the writing style of the organization. ",
            backstory="You are an editor who receives a blog post "
                      "from the Content Writer. "
                      "Your goal is to review the blog post "
                      "to ensure that it follows journalistic best practices,"
                      "provides balanced viewpoints "
                      "when providing opinions or assertions, "
                      "and also avoids major controversial topics "
                      "or opinions when possible.",
            allow_delegation=False,
            max_iter=5,
            verbose=True
        )
