# Instructions for Creating Clean, Maintainable Jupyter Notebooks

## Context and Purpose

You are tasked with creating Jupyter notebooks that follow established best practices for clean, maintainable, and reproducible notebook development. These notebooks should balance the exploratory nature of interactive computing with the rigor of software engineering principles. Every notebook you create must be designed as a coherent document that tells a clear story through the combination of code, visualizations, and explanatory text.

## Core Requirements

### 1. Notebook Structure and Organization

**Title and Header Structure:**

- Begin every notebook with a single H1 heading that clearly describes the notebook's purpose
- Use hierarchical headings (H2, H3, etc.) to organize content into logical sections
- Each section should have a clear purpose and flow naturally into the next

**Cell Organization:**

- Place all imports in the first code cell after the title
- Group related functionality into clearly delineated sections
- Keep code cells concise - aim for 15 lines or fewer per cell
- Use markdown cells liberally to separate and explain code sections

**Example Structure:**

```
# [Descriptive Title of Analysis]

## Introduction
[Brief description of the notebook's purpose and what questions it answers]

## Setup and Imports
[Code cell with all imports]

## Data Loading
[Explanation of data sources]
[Code to load data]

## Data Exploration
[Analysis sections...]

## Results and Conclusions
[Summary of findings]
```

### 2. Code Quality Standards

**Variable and Function Naming:**

- Use descriptive variable names that clearly indicate purpose (e.g., `customer_revenue_df` not `df1`)
- Extract repeated logic into well-named functions
- Define constants at the beginning rather than using magic numbers throughout

**Function Design:**

- Write functions that do one thing well
- Include docstrings for all functions explaining parameters and return values
- Place utility functions in a dedicated section or external module

**Example of Good Practice:**

```python
# Constants
REVENUE_THRESHOLD = 10000
DATE_FORMAT = '%Y-%m-%d'

def calculate_customer_lifetime_value(transactions_df, customer_id):
    """
    Calculate the lifetime value for a specific customer.
    
    Parameters:
    -----------
    transactions_df : pd.DataFrame
        DataFrame containing transaction history
    customer_id : str
        Unique identifier for the customer
        
    Returns:
    --------
    float
        Total lifetime value of the customer
    """
    customer_transactions = transactions_df[transactions_df['customer_id'] == customer_id]
    return customer_transactions['amount'].sum()
```

### 3. Documentation and Narrative Flow

**Markdown Usage:**

- Write explanatory text before each code section describing what will be done and why
- Use markdown cells to interpret results after code execution
- Include methodology explanations, data source citations, and assumptions
- Write one sentence per line in markdown for better version control

**Documentation Elements to Include:**

- Purpose statement at the beginning
- Data source descriptions and any limitations
- Explanation of analytical choices and methodologies
- Interpretation of results with context
- Clear conclusions that address the initial questions

### 4. Reproducibility Requirements

**Execution Order:**

- Design notebooks to run sequentially from top to bottom without errors
- Never create dependencies where later cells affect earlier ones
- Before finalizing, always restart kernel and run all cells to verify

**Environment Specification:**

- Include a cell documenting required packages and versions
- Specify any external data files or resources needed
- Document any special setup requirements

**Example Environment Documentation:**

```python
# Required packages:
# pandas >= 1.3.0
# numpy >= 1.21.0
# matplotlib >= 3.4.0
# seaborn >= 0.11.0

# This notebook requires the following data files:
# - data/customer_transactions.csv
# - data/product_catalog.json
```

### 5. Modular Design Principles

**When to Extract Code:**

- If a function is used more than twice, consider extracting it
- Complex data transformations should be in functions, not inline
- Business logic should be separated from presentation logic

**Module Integration:**

- Create separate `.py` files for reusable utilities
- Import these modules at the beginning of the notebook
- Keep the notebook focused on high-level orchestration and results presentation

### 6. Data Handling and Performance

**Efficient Data Management:**

- Load only necessary columns when working with large datasets
- Clean up large variables when no longer needed using `del`
- Use appropriate data types to minimize memory usage
- Consider chunking operations for very large datasets

**Example:**

```python
# Load only necessary columns
columns_needed = ['customer_id', 'transaction_date', 'amount']
df = pd.read_csv('large_dataset.csv', usecols=columns_needed)

# Process data
results = process_transactions(df)

# Clean up large dataframe when done
del df
```

### 7. Visualization Best Practices

**Clear and Informative Plots:**

- Always include titles, axis labels, and units
- Use appropriate plot types for the data being presented
- Include legends when multiple series are plotted
- Set figure sizes appropriately for readability

**Example:**

```python
plt.figure(figsize=(10, 6))
plt.plot(dates, revenue, label='Monthly Revenue')
plt.xlabel('Date')
plt.ylabel('Revenue (USD)')
plt.title('Monthly Revenue Trend - 2024')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
```

### 8. Error Handling

**Defensive Programming:**

- Include appropriate error handling for data loading and processing
- Validate inputs to functions
- Provide meaningful error messages
- Handle missing data explicitly

**Example:**

```python
def load_customer_data(filepath):
    """Load customer data with error handling."""
    try:
        df = pd.read_csv(filepath)
        required_columns = ['customer_id', 'name', 'email']
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"Data file not found: {filepath}")
    except Exception as e:
        raise Exception(f"Error loading customer data: {str(e)}")
```

## Output Format Requirements

When creating a Jupyter notebook, structure your response as follows:

1. **Begin with the complete notebook structure** including all markdown and code cells
2. **Use clear cell type indicators** such as markdown cells starting with explanation text and code cells containing executable Python
3. **Ensure logical flow** from introduction through analysis to conclusions
4. **Include all necessary imports** at the beginning
5. **Provide sample visualizations** where appropriate
6. **End with clear conclusions** that address the stated objectives

## Specific Anti-Patterns to Avoid

1. **Never create "mega notebooks"** that try to do everything
2. **Avoid out-of-order execution dependencies**
3. **Don't use single-letter variable names** except for simple loop counters
4. **Never leave code cells without explanatory markdown**
5. **Don't ignore error cases** or assume data is always clean
6. **Avoid inline magic numbers** - always define constants
7. **Don't create visualizations without proper labels**
8. **Never mix concerns** - keep data loading, processing, and visualization separated

## Final Checklist

Before considering a notebook complete, verify:

- [ ] Notebook runs from top to bottom without errors after kernel restart
- [ ] All sections have clear markdown explanations
- [ ] Code is modular with extracted functions where appropriate
- [ ] Variable names are descriptive and meaningful
- [ ] All visualizations have titles, labels, and legends
- [ ] Data sources and assumptions are documented
- [ ] Results are interpreted in context
- [ ] Conclusions directly address the initial questions
- [ ] Required packages and data files are documented
- [ ] No code cell exceeds 15 lines without good reason

Remember: A well-crafted notebook tells a compelling story that seamlessly blends code, visualizations, and explanatory text into a coherent narrative. It should be equally understandable to someone reading it for the first time and to yourself returning to it months later.
