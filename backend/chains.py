from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

class Chain:
    def __init__(self, retriever, llm):
        # custom_prompt = ChatPromptTemplate.from_template("""Use the following context to answer the question. 
        # If you don't know the answer based on the context, say you don't know.
        # Provide specific details from the context to support your answer.

        # Context:
        # {context}

        # Question: {question}

        # Answer:""")
        custom_prompt = ChatPromptTemplate.from_template("""
            You are an expert anime recommender. Your job is to help users find the perfect anime based on their preferences.

            Using the following context, provide a detailed and engaging response to the user's question.

            For each question, suggest exactly three anime titles. For each recommendation, include:
            1. The anime title.
            2. A concise plot summary (2-3 sentences).
            3. A clear explanation of why this anime matches the user's preferences.

            Present your recommendations in a numbered list format for easy reading.

            If you don't know the answer, respond honestly by saying you don't know — do not fabricate any information.

            Context:
            {context}

            User's question:
            {question}

            Your well-structured response:
        """)
        
        self.rag_chain_lcel=({"context":retriever | format_docs, "question": RunnablePassthrough()}  | custom_prompt | llm | StrOutputParser())


    # @staticmethod
    # def format_docs(docs):
    #     return "\n\n".join(doc for doc in docs)
    

    def invoke(self, query):
        print(query)
        return self.rag_chain_lcel.invoke(query)