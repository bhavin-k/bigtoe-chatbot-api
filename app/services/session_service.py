from typing import Dict, List
from app.core.database import get_mysql_connection
from langchain_openai import ChatOpenAI
from app.core.config import settings
import pandas as pd
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SessionService:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4.1", temperature=0.2, api_key=settings.OPENAI_API_KEY)
    
    def generate_query(self, query_input: str, provider_id: str) -> str:
        """Generate SQL query based on user input"""
        
        prompt = f"""You are an AI assistant that generates a SQL query based on the user's question by using {provider_id}.
            
            User question: "{query_input}"
            
            **'session_providers'** Table Schema OF mySQL database:
            +------------------------------+------------------+------+-----+---------+----------------+
            | Field                        | Type             | Null | Key | Default | Extra          |
            +------------------------------+------------------+------+-----+---------+----------------+
            | session_provider_id          | int              | NO   | PRI | NULL    | auto_increment |
            | session_id                   | int              | NO   | MUL | NULL    |                |
            | notes                        | text             | NO   |     | NULL    |                |
            | additional_tip               | varchar(50)      | NO   |     | NULL    |                |
            | additional_tip_pi_id         | varchar(255)     | NO   |     | NULL    |                |
            | provider_id                  | bigint           | NO   | MUL | NULL    |                |
            | class_date                   | date             | YES  |     | NULL    |                |
            | time                         | varchar(255)     | NO   |     | NULL    |                |
            | duration                     | varchar(255)     | NO   |     | 60      |                |
            | session_status               | varchar(255)     | NO   |     | assigned|                |
            | skill_id                     | int              | NO   | MUL | 29      |                |
            | confirmation_time            | datetime         | NO   |     | NULL    |                |
            | confirmation_mode            | varchar(30)      | NO   |     | NULL    |                |
            | rating                       | float(11,2)      | NO   |     | 0.00    |                |
            | client_rating                | float(11,2)      | NO   |     | 0.00    |                |
            | review                       | text             | NO   |     | NULL    |                |
            | client_review                | text             | NO   |     | NULL    |                |
            | qualities                    | varchar(255)     | NO   |     | NULL    |                |
            | client_short_review          | varchar(255)     | NO   |     | NULL    |                |
            +------------------------------+------------------+------+-----+---------+----------------+
            
            **'teacher'** Table Schema OF mySQL database:
            +--------------------+---------------------+------+-----+---------+----------------+
            | Field              | Type                | Null | Key | Default | Extra          |
            +--------------------+---------------------+------+-----+---------+----------------+
            | teacher_id         | bigint              | NO   | PRI | NULL    | auto_increment |
            | firstname          | varchar(255)        | NO   |     | NULL    |                |
            | lastname           | varchar(255)        | NO   |     | NULL    |                |
            | email              | varchar(255)        | NO   |     | NULL    |                |
            | expertise          | varchar(255)        | NO   |     | NULL    |                |
            | certified          | varchar(255)        | NO   |     | NULL    |                |
            | password           | text                | NO   |     | NULL    |                |
            | dob                | date                | YES  |     | NULL    |                |
            | gender             | enum('Male','Female')| NO  |     | Male    |                |
            | city               | varchar(255)        | YES  |     | NULL    |                |
            | state_code         | varchar(20)         | YES  |     | NULL    |                |
            | zipcode            | varchar(20)         | YES  |     | NULL    |                |
            | country            | varchar(255)        | YES  |     | NULL    |                |
            | country_code       | varchar(50)         | YES  |     | NULL    |                |
            | phone_no           | varchar(20)         | YES  |     | NULL    |                |
            | website            | varchar(255)        | YES  |     | NULL    |                |
            | instagram          | varchar(255)        | YES  |     | NULL    |                |
            | role               | varchar(20)         | YES  |     | NULL    |                |
            | avg_rating         | float(11,2)         | YES  |     | NULL    |                |
            | number_of_ratings  | int                 | YES  |     | NULL    |                |
            | time_zone          | varchar(50)         | NO   |     | NULL    |                |
            +--------------------+---------------------+------+-----+---------+----------------+
            
            **'private_classes'** Table Schema OF mySQL database:
            +------------------------------+---------------+------+-----+---------+----------------+
            | Field                        | Type          | Null | Key | Default | Extra          |
            +------------------------------+---------------+------+-----+---------+----------------+
            | private_class_id             | int           | NO   | PRI | NULL    | auto_increment |
            | notes                        | text          | NO   |     | NULL    |                |
            | student_id                   | bigint        | NO   | MUL | NULL    |                |
            | number_of_people             | int           | NO   |     | 1       |                |
            | is_couple                    | tinyint(1)    | NO   |     | 0       |                |
            | price                        | varchar(255)  | NO   |     | NULL    |                |
            | session_price                | varchar(255)  | NO   |     | NULL    |                |
            | time                         | varchar(255)  | NO   |     | NULL    |                |
            | duration                     | varchar(255)  | NO   |     | 60      |                |
            | status                       | varchar(20)   | NO   |     | Pending |                |
            | skill_id                     | int           | NO   | MUL | 29      |                |
            | gender                       | varchar(20)   | NO   |     | Open-Minded |            |
            | no_of_providers              | int           | NO   |     | 0       |                |
            | booking_time                 | timestamp     | NO   |     | CURRENT_TIMESTAMP |      |
            | confirmation_time            | datetime      | NO   |     | NULL    |                |
            | cancellation_time            | datetime      | NO   |     | NULL    |                |
            | confirmation_mode            | varchar(30)   | NO   |     | NULL    |                |
            | canceled_by                  | varchar(30)   | NO   |     | NULL    |                |
            | general_search               | tinyint(1)    | NO   |     | 1       |                |
            +------------------------------+---------------+------+-----+---------+----------------+
            
            **'competencies'** Table Schema OF mySQL database:
            +------------------------+---------------+------+-----+---------+----------------+
            | Field                  | Type          | Null | Key | Default | Extra          |
            +------------------------+---------------+------+-----+---------+----------------+
            | skill_id               | int           | NO   | PRI | NULL    | auto_increment |
            | skills                 | varchar(255)  | NO   |     | NULL    |                |
            | display_string_client  | varchar(255)  | NO   |     | NULL    |                |
            | display_string_provider| varchar(255)  | NO   |     | NULL    |                |
            | service_category_id    | int           | NO   | MUL | NULL    |                |
            | competency_category    | int           | NO   |     | 0       |                |
            | capacity               | varchar(100)  | NO   |     | NULL    |                |
            | created_at             | timestamp     | NO   |     | CURRENT_TIMESTAMP |      |
            +------------------------+---------------+------+-----+---------+----------------+
            
            **'student_address'** Table Schema OF mySQL database:
            +------------------------+-------------------+------+-----+---------+----------------+
            | Field                  | Type              | Null | Key | Default | Extra          |
            +------------------------+-------------------+------+-----+---------+----------------+
            | student_address_id     | int               | NO   | PRI | NULL    | auto_increment |
            | student_id             | bigint            | NO   | MUL | NULL    |                |
            | locationtype           | varchar(100)      | NO   |     | NULL    |                |
            | residencetype          | varchar(100)      | NO   |     | NULL    |                |
            | locationname           | varchar(255)      | NO   |     | NULL    |                |
            | street_address         | varchar(255)      | NO   |     | NULL    |                |
            | new_formatted_address  | varchar(255)      | NO   |     | NULL    |                |
            | unit_number            | varchar(100)      | YES  |     | NULL    |                |
            | stu_add_city           | varchar(100)      | NO   |     | NULL    |                |
            | state                  | varchar(100)      | NO   |     | NULL    |                |
            | zipcode                | varchar(50)       | NO   |     | NULL    |                |
            | country                | varchar(50)       | NO   |     | NULL    |                |
            | neighborhood           | varchar(255)      | YES  |     | NULL    |                |
            +------------------------+-------------------+------+-----+---------+----------------+
            
            **'service_categories'** Table Schema OF mySQL database:
            +------------------------+--------------+------+-----+---------+----------------+
            | Field                  | Type         | Null | Key | Default | Extra          |
            +------------------------+--------------+------+-----+---------+----------------+
            | service_categories_id  | int          | NO   | PRI | NULL    | auto_increment |
            | service_category       | varchar(255) | NO   |     | NULL    |                |
            +------------------------+--------------+------+-----+---------+----------------+

            **Mapping of Tables:**(Most important - to understand how tables are related)
            1. session_providers.provider_id -> maps to -> teacher.teacher_id
            (Many session_providers entries can belong to one teacher)

            2. session_providers.session_id -> maps to -> private_classes.private_class_id
            (Many session_providers can be linked to one private_class for personal details)

            3. session_providers.skill_id -> maps to -> competencies.skill_id
            (Many session_providers can reference one skill in the competencies table)

            4. private_classes.location -> maps to -> student_address.student_address_id
            (Each private class location is tied to a student address entry)

            5. competencies.service_category_id -> maps to -> service_categories.service_categories_id
            (Each skill (competency) belongs to a specific service category)
            
            
            Generate a SQL query that retrieves the relevant data from the database.
            Ensure the query is syntactically correct and optimized for performance.
            
            **Important Notes:**
            - Please understand the user's **query_input intent** carefully. based on them write a query.
            - **Remember today's date** is {datetime.now().strftime('%Y-%m-%d')}.
            - If user is asking about their past sessions, then only those sessions which are in the past should be returned.
            - If user is asking about future sessions, then only those sessions which are in the future should be returned.
            - The query should only include fields that are relevant to the user's question.
            - Do not forget provided **provider_id**
            - Do not mistake column names table name spelling in provided schema.
            - The query should be written in standard SQL syntax.
            - class_date is a session_confirmed_date, it is to track past sessions, so use it to filter results based on time ranges if applicable.
            - rating is decimal(3,2) and should be used to filter or sort results based on user ratings.
            - Always put maximum as limit 10 even if user specified large number in the query to avoid returning too many results if more than one row are there in results.
            - On query always put db name 'fitness_database' then using '.' access table name like 'fitness_database.session_providers' instead of just 'session_providers'.
            - When using a select on subquery don't use the table name put the field name directly.
            - Only return those fields that are **relevant to the user query**. Not all the fields from the tables.
            
            
            ** Following Columns Fields that cover most of the user queries:** (So keep around them)
            - session_providers: provider_id, session_provider_id, session_id, session_confirmed_date (class_date), time, session_status, duration, additional_tip, rating, client_review, qualities, review
            - teacher: firstname, gender
            - student_address: locationtype, stu_add_city(is the city- take from this table), state, zipcode, neighborhood
            - competencies: skills
            - service_categories: service_category
            - private_classes: number_of_people, is_couple, general_search
            
            Example user questions:
            - "What were my last 3 sessions?" - In this type of question, only return some of fileds like session_confirmed_date(is a class_date from session_providers table), time(from session_providers table), 
            locationtype(from student_address table), service_category(from service_categories table), duration(from student_address table), skills(from competencies table), firstname(from teacher table), rating(from session_providers table), review(from session_providers table).
            - "Provide me last 5 dates of sessions" - In this type of question, only return unique session_confirmed_date(is a class_date from session_providers table)
            return **Only MySQL Query** without any extra words like 'sql' or any other explanation.
            - "How much total duration you spent on last 5 sessions?" - return the individual durations sum of the last 5 sessions.'
            """
        
        try:
            generated_query = self.llm.predict(prompt).strip()
            logger.info(f"Generated query: {generated_query}")
            return generated_query
        except Exception as e:
            logger.error(f"Error generating query: {str(e)}")
            raise e

    def process_session_query(self, query: str, provider_id: str) -> Dict:
        """Process session-related query"""
        try:
            logger.info(f"Processing session query: {query}")
            
            sql_query = self.generate_query(query, provider_id)
            logger.info(f"Generated SQL query: {sql_query}")
            
            conn = get_mysql_connection()
            cursor = conn.cursor(dictionary=True)
            
             # Ensure the query uses the default database 'fitness_database'
            if not sql_query.lower().startswith("use fitness_database;"):
                cursor.execute("USE fitness_database;")
            cursor.execute(sql_query)
            results = cursor.fetchall()
            cursor.close()
            
            df_results = pd.DataFrame(results) 
            logger.info(f"Query returned: {len(df_results)} records")
            
            # Return both SQL query and results
            return {
                "sql_query": sql_query,
                "results": df_results.to_dict(orient="records"),
                "record_count": len(df_results)
            }
            
        except Exception as e:
            logger.error(f"Error processing session query: {str(e)}")
            raise e

    def get_initial_message(self, provider_id: str) -> str:
        """Get initial greeting message"""
        try:
            conn = get_mysql_connection()
            cursor = conn.cursor(dictionary=True)
            
            sql_query = f"SELECT * FROM fitness_database.teacher WHERE teacher_id = {provider_id};"
            cursor.execute(sql_query)
            results = cursor.fetchall()
            cursor.close()
            
            if results and len(results) > 0:
                firstname = results[0].get('firstname', '')
                return f"Hey {firstname}, I'm BigToe AI assistant. Let me know what you need assistance with!"
            else:
                return "Hey! I'm BigToe AI assistant. How can I help you today?"
                
        except Exception as e:
            logger.error(f"Error getting initial message: {str(e)}")
            return "Hey! I'm BigToe AI assistant. How can I help you today?"

    def format_session_response(self, query: str, session_data: Dict) -> str:
        """Synthesize response from session data"""
        
        # Extract the actual results from the session_data dictionary
        actual_results = session_data.get("results", []) if session_data else []
        sql_query = session_data.get("sql_query", "") if session_data else ""
        record_count = session_data.get("record_count", 0) if session_data else 0
        
        prompt =  f"""You are an assistant summarizing session history for a user query. Use the session data and instructions below to respond helpfully and professionally.

            User Question:
            {query}

            Session History:
            {actual_results}

            SQL Query Used:
            {sql_query}

            Record Count: {record_count}

            **Instructions for Response:**

            - Provide a concise, relevant answer based on the session data.
            - Automatically infer and apply the appropriate response format depending on the structure and content of session_data.
              - Response format can be in **text** or **table** format.
              - If session_data has rows with much more columns, show only essential fields in the table format like: Date, Time, Location (City, State), Service Type(as service_category), Duration, Rating, Client Review
            - If the query asks for specific details, return them in a well-structured format.
            - If particular fields is there in session_data, ensure that they haven't duplication in the response. if there is duplication, then remove it. return only unique values.
            - Do not write anything like, 'Note: ...' or 'Please note that...' in the response.
            - Include the SQL query used at the end of the response for transparency (in a code block format).

            **Important:** (Alays keep in mind current date)
            - Today's date: {datetime.now().strftime('%Y-%m-%d')}
            - Do not include any information that is not relevant to the user query. Unnecessary details must be avoided.
            - Even you can include those information only from the session data which is relevant to the user query(state["query"]).
            - If, In state["query"]  user is asking about large number of sessions, then always put message like "I can only provide you the last 10 sessions" message at last. below that return session data in suitable format.
            
            **Examples of response behavior**:
            - Query: "Can you provide me last few session dates?" - Return just the **dates**, like:
                - "Here are the dates of your last few sessions:"
                    - 2024-03-22
                    - 2022-07-08
                    - 2022-06-10
           - Query: "How many sessions did I do last year?" - Treat "last year" as the full **calendar year immediately before today's date**. For example, if today is 2025-05-23, then "last year" means 2024-01-01 to 2024-12-31. 
                - First check if there are any sessions in that specific year.
                - If the query asks for the count, return the total number of sessions only.
                - If the query asks for details, return a table of sessions from that year.
                - If no sessions exist in that calendar year, respond: 
                    **"There are no sessions conducted in [year]"**.
            - Query: "Can I get last 2 sessions in table format?" - Return table with 2 most recent sessions.
            - Query: How long was the last session? - Return just the **duration(minutes)** of the last session ,with formatted text.
            - Query: "What was the rating of my last session?" - Return just the **rating** of the last session.
            
           """
        
        try:
            logger.info(f"Today's date: {datetime.now().strftime('%Y-%m-%d')}")
            response = self.llm.predict(prompt)
            
            # Add SQL query information at the end
            formatted_response = f"{response.strip()}"
            
            logger.info(f"Formatted response: {formatted_response}")
            return formatted_response
            
        except Exception as e:
            logger.error(f"Error synthesizing session response: {str(e)}")
            return f"I encountered an error while accessing your session history: {str(e)}"