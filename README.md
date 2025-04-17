# Local Network Chat Application

This project is a simple local network chat application built with Python using the CustomTkinter UI library. It allows users to connect with each other within a local network and send/receive messages. Users can either discover available peers or manually enter an IP address to initiate communication.

## Table of Contents
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [Contributing](#contributing)
- [Guidelines](#guidelines)

## Installation

### Step 1: Fork the Repository
Fork this repository to your GitHub account by clicking on the **Fork** button on the top-right of the page.

### Step 2: Clone the Repository
Clone the forked repository to your local machine using Git. Run the following command in your terminal:
```bash
git clone https://github.com/yourusername/repository-name.git
```

### Step 3: Install Dependencies
Navigate to the project directory and install the required dependencies using the following command:
```bash
cd repository-name
pip install -r requirements.txt
```

This will install all the necessary libraries and dependencies for running the project.

### Step 4: Run the Application
Once all dependencies are installed, you can run the application using:
```bash
python gui.py
```

## Project Structure

Here’s an overview of the project structure:

```
gui.py
objects.py
README.md
requirements.txt
service.py
```

### File Descriptions:

- **`gui.py`**: Contains the UI code using CustomTkinter. It is responsible for handling user interface components and connecting them to the business logic. This file provides the layout for chat, discovery, and connecting screens.
  
- **`objects.py`**: Contains the data classes for the application such as `User`, `Message`, `ConnectionSuccess`, and `ConnectionFailure`. These objects represent the structure of users, messages, and connection states.
  
- **`requirements.txt`**: A list of Python dependencies required to run the project. It includes libraries like `customtkinter`, `threading`, and `random`.
  
- **`service.py`**: This file contains the `ChatService` class, which manages all the business logic of the chat application. It handles message sending/receiving, user discovery, and connection management.

- **`.gitignore`**: A file that specifies files and directories that should be ignored by Git. It includes entries for temporary files, `__pycache__`, and other unnecessary files.

## Usage

1. **Run the application**: 
   After setting up the environment, run the application by executing the following command:
   ```bash
   python gui.py
   ```

## Contributing

Please follow these steps to contribute:

1. **Fork the repository** to your GitHub account.
2. **Clone your fork** to your local machine.
3. **Make your changes** and commit them with clear, concise messages.
   ```bash
   git add .
   git commit -m "Describe your changes"
   ```
4. **Push your changes** to your forked repository:
   ```bash
   git push origin your-feature-branch
   ```
5. **Create a pull request**: Open a pull request to the `main` branch of the original repository.

## Guidelines

### Separate UI and Business Logic

In this project, the business logic (i.e., managing connections, fetching users, sending/receiving messages) is handled by the `ChatService` class located in `service.py`. The user interface (UI) is handled separately in `gui.py`. This separation follows the **MVC (Model-View-Controller)** principle, where:

- **Model** (`objects.py`) defines data structures like `User`, `Message`, `ConnectionSuccess`, etc.
- **View** (`gui.py`) defines the layout, components, and interactions that the user will see.
- **Controller** (`service.py`) contains the logic for managing data and interactions between the UI and model.

### Writing UI Code:
- Keep UI-related logic in `gui.py` and focus on defining the appearance, layout, and interaction logic.
- Use the `ChatService` class to get data (e.g., users, messages) or trigger actions (e.g., sending a message) from the UI.

### Writing Business Logic:
- All core logic, like managing users, sending/receiving messages, and connecting to peers, should be written in `service.py`.
- The UI should interact with the business logic by calling methods of the `ChatService` class and passing the required data.

By keeping UI and business logic separate, you can easily maintain and expand the project in the future.