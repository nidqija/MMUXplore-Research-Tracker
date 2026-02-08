MMU Xplore Research Paper Tracker
This guide details the steps to set up, configure, and run the MMU Xplore Research Paper Tracker project locally.

1. Clone the Repository
Start by cloning the codebase to your local machine.

Bash
git clone <'https://github.com/nidqija/MMUXplore-Research-Tracker.git'>
cd <your-project-folder>
2. Create & Activate Virtual Environment
It is recommended to use a virtual environment to manage dependencies isolated from your system Python.

Bash
# Create the virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows:
source .venv/Scripts/activate

3. Install Dependencies
Install the required Python packages listed in the requirements file.

Bash
pip install -r requirements.txt
4. Database Setup
Before running the server, you must apply the database migrations. 
Bash
# Apply migrations to set up the database schema
python manage.py migrate

Note: If you have made changes to the models.py files, run python manage.py makemigrations before running migrate.

5. Run the Server
Ensure you are in the directory containing manage.py and start the development server.

Bash
python manage.py runserver
You can now access the project at http://127.0.0.1:8000/.
