## Overview
The Robocasa Plan UI is a web application designed to facilitate the creation and management of plans for a robotic dishwasher. It allows users to input item details, generate simple and actual plans, and view the results in a user-friendly interface.

## Project Structure
The project is divided into two main parts: the backend and the frontend.

### Backend
- **app.py**: Entry point for the Flask server, initializing routes for plan generation.
- **data_structures.py**: Defines the data structures used in the application, including classes for items, plans, tasks, and actions.
- **mismatch_finder.py**: Contains functions to find mismatches between generated plans for validation and debugging.
- **plan_generator.py**: Includes functions for generating simple and actual plans based on provided items and their attributes.
- **requirements.txt**: Lists the Python dependencies required for the backend application.
- **routes/plans.py**: Defines the API endpoints for creating and retrieving plans.

### Frontend
- **src/main.ts**: Entry point for the Vue.js application, initializing the Vue instance.
- **src/App.vue**: Root component serving as the main layout for the application.
- **src/components/ItemForm.vue**: Component for inputting item details (type, size, position, fragility).
- **src/components/PlanControls.vue**: Component containing controls for generating plans.
- **src/components/PlanDisplay.vue**: Component for displaying generated plans.
- **src/services/api.ts**: Functions for making API calls to the backend.
- **src/types/index.ts**: TypeScript interfaces for data structures used in the frontend.

## Setup Instructions

### Backend
1. Navigate to the `backend` directory.
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the Flask server:
   ```
   python app.py
   ```

### Frontend
1. Navigate to the `frontend` directory.
2. Install the required dependencies:
   ```
   npm install
   ```
3. Start the development server:
   ```
   npm run serve
   ```

## Usage
- Open your web browser and navigate to `http://localhost:3000` to access the application.
- Use the Item Form to input details about the items you want to load into the dishwasher.
- Click the buttons in the Plan Controls to generate simple and actual plans.
- View the generated plans in the Plan Display component.
