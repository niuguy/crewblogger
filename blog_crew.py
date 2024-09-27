
import os
import re
from crewai import Crew
from blog_agents import BlogAgents
from blog_tasks import BlogTasks
from crewai import Process


def create_blog_post(topic, sub_topics):
    agents = BlogAgents()
    tasks = BlogTasks()
    chief_writer_agent = agents.writer_chief_agent()
    senior_writer_agent = agents.writer_senior_agent()

    crew_tasks = []
    write_draft_task = tasks.write_draft_task(chief_writer_agent, topic, sub_topics)
    crew_tasks.append(write_draft_task)

    for num, sub_topic in enumerate(sub_topics):
        section_task = tasks.write_section_task(senior_writer_agent, num, sub_topic)
        crew_tasks.append(section_task)

    crew = Crew(
        agents=[chief_writer_agent, senior_writer_agent],
        tasks=crew_tasks,
        process_type=Process.sequential,
        max_rpm=3,
        share_crew=True,
        logging=True,
        output_log_file="./logs/blogger.log"
    )
    
    result = crew.kickoff()
    print(result)
    print(crew.usage_metrics)

    # Compose final article
    final_draft_content = compose_final_article('./output/draft.md', './output')
    return final_draft_content



def compose_final_article(draft_path, sections_dir):
    # Read the draft
    with open(draft_path, 'r', encoding='utf-8') as f:
        draft_content = f.read()

    # Remove the markdown header and footer
    draft_content = draft_content.replace('```markdown', '')
    draft_content = draft_content.replace('```', '')    


    # Find all placeholders
    placeholders = re.findall(r'##\[SECTION_CONTENT_\d+\]##', draft_content)

    # Read all section files
    section_files = sorted([f for f in os.listdir(sections_dir) if f.startswith('section-') and f.endswith('.md')])

    # Replace placeholders with section content
    for i, placeholder in enumerate(placeholders):
        if i < len(section_files):
            with open(os.path.join(sections_dir, section_files[i]), 'r', encoding='utf-8') as section_file:
                section_content = section_file.read()
                draft_content = draft_content.replace(placeholder, section_content, 1)


    # Write the final article
    final_article_path = os.path.join(sections_dir, 'final-article.md')
    with open(final_article_path, 'w', encoding='utf-8') as f:
        f.write(draft_content)

    return draft_content