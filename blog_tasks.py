from crewai import Task


class BlogTasks():
    def write_draft_task(self, agent, topic, sub_topics):
        return Task(
            description=f"""Draft an insightful article outline on {topic} structured as introduction, body sections, and conclusion.
            1. Write an introduction that provides a brief overview of the topic and its importance (150-200 words).
            2. For the body, create section headers using the following sub-topics: {sub_topics}
               Under each section header, add the placeholder '##[SECTION_CONTENT_i]##' where i is the section number.
            3. Write a conclusion that summarizes the key points (100-150 words).
            
            Format the entire draft in Markdown.""",
            expected_output="A well-structured article outline in Markdown format with placeholders for section content.",
            output_file="./output/draft.md",
            agent=agent,
        )

    def write_section_task(self, agent, topic_num, sub_topic):
        return Task(
            description=f"""Write a detailed section on the sub-topic: "{sub_topic}"
            1. The section should be at least 200 words.
            2. Incorporate relevant information, examples, and insights.
            3. Use citation links within the content where appropriate.
            4. Ensure a smooth transition to the next section at the end.
            5. Format the section in Markdown.
            
            Do not include a section header or conclusion paragraph, as this is part of a larger article.""",
            expected_output=f"A detailed section on '{sub_topic}' with at least 200 words, formatted in Markdown.",
            output_file=f"./output/section-{topic_num}.md",
            agent=agent
        )



