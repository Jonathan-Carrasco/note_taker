# Alpaca Health Software Engineering Take-Home Project

### Project Description

Visit this link for details:
[https://harviio.notion.site/Alpaca-Health-Eng-Take-home-Project-1411bfc50b90803382d4cae01f9bcf18?pvs=4](https://www.notion.so/harviio/ABA-Session-Note-Generator-Take-Home-Project-1411bfc50b90803382d4cae01f9bcf18?pvs=4)

## Setup Instructions

### Backend Setup (Python 3.11+ required)

```bash
# Create and activate virtual environment
python -m venv alpaca_venv
source alpaca_venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export OPENAI_API_KEY=your-openai-api-key-here

# Start the server
fastapi dev main.py
```

### Frontend Setup (Node.js 18+ required)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The application will be available at:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Default Project Structure

- `frontend/`: Next.js application
  - `src/components/`: Reusable React components
  - `src/app/`: Next.js app router pages
- `backend/`: FastAPI application
  - `app/main.py`: API endpoints

## Development

- Frontend runs on port 3000 with hot reload enabled
- Backend runs on port 8000 with auto-reload enabled
- API documentation available at http://localhost:8000/docs

## Submission

1. Create a private GitHub repository
2. Implement your solution
3. Document any assumptions or trade-offs
4. Include instructions for running your solution
5. Send us the repository link

## Details

### Database Schema

The application uses a SQLite database with four core tables:

- **Patients**: Stores patient demographics (name, DOB, ICD code, address)
- **Clinics**: Manages clinic information (name, address)
- **BCBAs**: Board Certified Behavior Analysts data (name, credentials)
- **Session Notes**: Links patients, clinics, and BCBAs with appointment details (date, duration, notes)

### UX Components

The frontend allows a user to associate a note with a patient, and aggregates the session metadata into a user friendly readable template.:

- **SessionDetailsForm**: Patient/clinic selection, appointment scheduling, and new patient creation
- **NoteGenerationForm**: Observation input and AI-powered note generation using GPT-4o
- **NewPatientForm**: Modal-based patient registration workflow

The application features two main user flows:

1. **Generate Notes**: Multi-step form for session setup and AI note generation
2. **Saved Notes**: Comprehensive view with search, edit, and delete capabilities for existing session notes

### Backend Architecture

The backend follows a service-oriented architecture with dedicated services for each entity, a repository pattern for data access, and integration with OpenAI's GPT-4o model for generating structured ABA session notes following professional templates. Trade offs I made were allowing any BCBA to view all patient data. Ideally, we would only allow BCBAs to view patients that attend their clinic. In the interest of time I also didn't display all BCBAs as a dropdown. Ideally, this site uses authentication to identify which BCBA to display notes for. I created a template that I believed would act as a useful format through which to display notes. Metadata autopopulate this format, as well as relevant details form the session notes.

## Time Expectation

- Expected time: 3-4 hours
- Please don't spend more than 6 hours

## Evaluation Criteria

| Category                  | Details                                                                                                                                                                                     | Weight |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| Product sense and scoping | - Final product decisions alignment with requirements<br>- Appropriate deprioritization of non-crucial parts                                                                                | 10%    |
| Technology selection      | - Right tools chosen for the job                                                                                                                                                            | 10%    |
| Technical Level           | - Well-organized and intuitive code structure<br>- Modular code (e.g., React components used)<br>- Proper use of React hooks<br>- Good state management<br>- Correct use of useEffect hooks | 40%    |
| Craft and Quality         | - Usable and intuitive UI/UX<br>- Presence and severity of bugs                                                                                                                             | 20%    |
| Documentation             | - Clear communication of logic and technical decisions in README                                                                                                                            | 10%    |
| Testing                   | - Presence of tests<br>- Quality and robustness of tests                                                                                                                                    | 10%    |
