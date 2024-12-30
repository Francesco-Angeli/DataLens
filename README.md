# DataLens - Data Analysis and Visualization Platform
#### Video Demo: https://youtu.be/wInNv4Lrnbs
#### Description:
DataLens is a sophisticated web application designed to revolutionize how people interact with and understand statistical data. The project addresses a critical challenge in data interpretation: while finding individual statistics is relatively straightforward, understanding their broader context and implications often requires considerable effort and expertise.

The primary goal of DataLens is to bridge this gap by not only providing reliable statistical data but also automatically contextualizing it with related metrics and visualizations. For example, when a user queries about unemployment rates, the system doesn't just show the raw numbers - it automatically provides related economic indicators like wage growth, inflation rates, and sector-specific employment trends, enabling a more comprehensive and objective analysis.

### Key Features:

1. **Intelligent Data Analysis**: Leverages the Perplexity API to access and analyze data from authoritative sources
2. **Multi-Chart Visualization**: Automatically generates four interconnected charts:
   - Main trend visualization
   - Compositional breakdown (pie chart)
   - Two related metric charts for context
3. **Geographic Filtering**: Supports different geographic scopes (Italy, EU, World, Italian Regions)
4. **Time Range Selection**: Flexible time period selection with preset options
5. **Source Citations**: Transparent sourcing with links to original data
6. **User Authentication**: Secure account system for saving and reviewing past analyses

### Getting Started

#### Prerequisites
- Python 3.8 or higher
- SQLite 3
- Perplexity API key
- Modern web browser with JavaScript enabled

#### Installation and Setup

1. **Clone the repository**:
```bash
git clone https://github.com/Francesco-Angeli/DataLens.git
cd DataLens
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Environment Setup**:
   - Create a `.env` file in the project root
   - Add your Perplexity API key:
   ```
   PERPLEXITY_API_KEY=your_perplexity_api_key_here
   ```
   - You can get your API key from [Perplexity API](https://docs.perplexity.ai/)
   - Reference `.env.example` for required variables format

4. **Initialize the Database**:
```bash
sqlite3 stats.db
```

Then create the necessary tables by running these SQL commands:
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    hash TEXT NOT NULL
);

CREATE TABLE queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    query_text TEXT NOT NULL,
    response_text TEXT NOT NULL,
    graph_data TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
```

5. **Project Structure**:
```
DataLens/
├── app.py                 # Main application file
├── helpers.py            # Helper functions
├── requirements.txt      # Project dependencies
├── .env.example         # Environment variables template
├── static/              # Static assets
│   ├── styles/         # CSS files
│   └── background.js   # JavaScript files
└── templates/           # HTML templates
```

6. **Run the Application**:
```bash
flask run
```
The application will be available at `http://localhost:5000`

7. **First Use**:
   - Register a new user account
   - Log in to access the dashboard
   - Enter your data analysis query
   - Select geographic area and time range
   - View the generated visualizations and analysis

### Technical Implementation

The project is built using Flask and follows a clear architectural structure:

* **`app.py`**: The core application file containing:
  - Route definitions and request handling
  - User authentication logic
  - API integration with Perplexity
  - Database interactions
  - Response formatting and streaming

* **`helpers.py`**: Contains utility functions for:
  - Error handling
  - Login validation
  - API query formatting
  - Security measures

* **Templates Directory**: Organizes the frontend views:
  - `layout.html`: Base template with common elements
  - `index.html`: Main search interface
  - `results.html`: Data visualization page
  - `history.html`: Past queries viewer
  - Authentication templates (`login.html`, `register.html`, `change_password.html`)

* **Static Directory**: Contains frontend assets:
  - Modular CSS organization in components
  - JavaScript for interactive features
  - Animation definitions
  - Consistent styling variables

### Design Decisions

1. **API Choice**: Selected Perplexity API for its:
   - Comprehensive data access
   - Real-time analysis capabilities
   - Reliable source citations
   - High accuracy in data interpretation

2. **Four-Chart System**: Implemented a standardized four-chart visualization because:
   - Main trend chart provides historical context
   - Pie chart shows composition/distribution
   - Two related charts ensure comprehensive context
   - This combination consistently provides a complete story behind the numbers

3. **Frontend Architecture**:
The frontend adopts a minimalist, function-first approach with a component-based CSS structure to:
- Focus users' attention on data analysis
- Provide an intuitive interface for new users
- Maintain consistency across the application
- Enable easy styling modifications
- Ensure responsive design

4. **Security Implementation**:
   - Password hashing for user security
   - Session management for user state
   - Protected routes with login requirements
   - Secure API key handling through environment variables

5. **Database Design**:
The application uses SQLite for its simplicity and efficiency. The database schema consists of two main tables as described in the installation section.

This design was chosen for:
   - Simple deployment and maintenance
   - Efficient query history tracking
   - Robust user management
   - Easy backup and restoration

### Troubleshooting

Common issues and solutions:

1. **Database Errors**:
   - Ensure stats.db is properly initialized
   - Check file permissions
   - Verify SQL tables are created correctly

2. **API Issues**:
   - Confirm your API key is correct in .env
   - Check your internet connection
   - Verify API rate limits

3. **Session Errors**:
   - Clear flask_session directory
   - Restart the application

### Future Enhancements

1. **Data Source Integration**:
   - Integration with open-source statistical databases
   - Direct connection to official statistical APIs
   - Real-time data updates

2. **Advanced Statistical Analysis**:
   - Development of statistical correlations between different metrics
   - Impact analysis of events on various economic indicators
   - Mathematical modeling of cause-effect relationships

3. **Platform Improvements**:
   - Advanced data export capabilities
   - Custom visualization options
   - Comparative analysis between regions
   - User preferences customization

DataLens transforms data analysis from a simple number-lookup into an insightful journey of discovery. By automatically providing context and related metrics, it helps users develop a more nuanced and complete understanding of statistical trends and their implications.
