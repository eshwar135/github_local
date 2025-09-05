import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from transformers import pipeline
import warnings
warnings.filterwarnings('ignore')

class FreeCSVAnalyzer:
    def __init__(self):
        """Initialize free local models (no API keys required)"""
        print("🔄 Initializing free local models...")
        try:
            # Use small, efficient models that run on CPU
            self.text_generator = pipeline(
                "text-generation", 
                model="distilgpt2",
                device=-1,  # Use CPU (free)
                max_length=100
            )
            print("✅ Free text generator loaded successfully!")
        except Exception as e:
            print(f"⚠️ Could not load text generator: {e}")
            self.text_generator = None
        
    def analyze_csv(self, file_path, user_query):
        """Analyze CSV file and generate insights without paid APIs"""
        try:
            # Load data with encoding handling
            df = self._load_csv_safely(file_path)
            
            # Generate analysis based on query
            analysis = self._generate_analysis(df, user_query)
            
            return {
                'success': True,
                'data_info': self._get_data_info(df),
                'analysis': analysis,
                'html_output': self._create_html_output(analysis),
                'code': self._generate_analysis_code(df, user_query),
                'dataframe': df
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _load_csv_safely(self, file_path):
        """Load CSV with multiple encoding attempts"""
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                df = pd.read_csv(file_path, encoding=encoding, low_memory=False)
                print(f"✅ File loaded with {encoding} encoding")
                return df
            except UnicodeDecodeError:
                continue
        
        raise ValueError("Could not decode CSV file with any standard encoding")
    
    def _get_data_info(self, df):
        """Get comprehensive information about the dataset"""
        return {
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'sample_data': df.head(3).to_dict('records'),
            'missing_values': df.isnull().sum().to_dict(),
            'summary_stats': df.describe().to_dict() if len(df.select_dtypes(include=[np.number]).columns) > 0 else {},
            'memory_usage': df.memory_usage(deep=True).sum(),
            'unique_counts': {col: df[col].nunique() for col in df.columns}
        }
    
    def _generate_analysis(self, df, user_query):
        """Generate comprehensive analysis using local processing only"""
        results = []
        query_lower = user_query.lower()
        
        try:
            # Handle tweet analysis specifically
            if 'tweet' in query_lower and 'max' in query_lower and 'count' in query_lower:
                results.extend(self._analyze_tweets(df))
            
            # General count analysis
            elif 'count' in query_lower or 'max' in query_lower:
                results.extend(self._analyze_counts(df))
            
            # Group analysis
            elif 'group' in query_lower or 'by' in query_lower:
                results.extend(self._analyze_groups(df))
            
            # Time series analysis
            elif 'date' in query_lower or 'time' in query_lower:
                results.extend(self._analyze_temporal(df))
            
            # Statistical analysis
            elif any(word in query_lower for word in ['stats', 'statistics', 'summary', 'describe']):
                results.extend(self._analyze_statistics(df))
            
            # Default comprehensive analysis
            else:
                results.extend(self._analyze_general(df))
                
        except Exception as e:
            results.append(f"Analysis error: {str(e)}")
        
        return results
    
    def _analyze_tweets(self, df):
        """Analyze tweet data specifically"""
        results = []
        
        # Look for tweet-related columns
        user_col = self._find_column(df, ['user', 'username', 'author'])
        date_col = self._find_column(df, ['date', 'timestamp', 'created_at'])
        
        if user_col and date_col:
            try:
                # Convert date column to datetime
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                df['date_only'] = df[date_col].dt.date
                
                # Count tweets per user per day
                daily_counts = df.groupby([user_col, 'date_only']).size()
                max_tweets = daily_counts.max()
                max_users = daily_counts[daily_counts == max_tweets]
                
                results.append(f"📈 Maximum tweets per user per day: {max_tweets}")
                results.append(f"👥 Users with maximum tweets on specific days:")
                
                for (user, date), count in max_users.head(5).items():
                    results.append(f"  • {user} on {date}: {count} tweets")
                
                # Additional insights
                total_users = df[user_col].nunique()
                total_tweets = len(df)
                avg_tweets_per_user = total_tweets / total_users if total_users > 0 else 0
                
                results.append(f"📊 Total users: {total_users}")
                results.append(f"📊 Total tweets: {total_tweets}")
                results.append(f"📊 Average tweets per user: {avg_tweets_per_user:.2f}")
                
            except Exception as e:
                results.append(f"Tweet analysis error: {str(e)}")
        else:
            results.append("⚠️ Could not find user or date columns for tweet analysis")
            
        return results
    
    def _analyze_counts(self, df):
        """Analyze counts and maximums"""
        results = []
        
        # Numeric columns analysis
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols[:3]:  # Limit to first 3 numeric columns
            results.append(f"📊 {col}: Max = {df[col].max()}, Min = {df[col].min()}")
        
        # Categorical columns analysis
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols[:3]:  # Limit to first 3 categorical columns
            value_counts = df[col].value_counts()
            results.append(f"🏷️ {col}: Most frequent = '{value_counts.index[0]}' ({value_counts.iloc[0]} times)")
        
        return results
    
    def _analyze_groups(self, df):
        """Analyze groupings in data"""
        results = []
        
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            for col in categorical_cols[:2]:  # Analyze first 2 categorical columns
                grouped = df.groupby(col).size().sort_values(ascending=False)
                results.append(f"📋 Groups in {col}:")
                for group, count in grouped.head(5).items():
                    results.append(f"  • {group}: {count} records")
        
        return results
    
    def _analyze_temporal(self, df):
        """Analyze temporal patterns"""
        results = []
        
        date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
        for col in date_cols[:1]:  # Analyze first date column
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                date_range = df[col].max() - df[col].min()
                results.append(f"📅 {col}: Spans {date_range.days} days")
                
                # Daily counts
                daily_counts = df[col].dt.date.value_counts()
                results.append(f"📅 Peak activity date: {daily_counts.index[0]} ({daily_counts.iloc[0]} records)")
                
            except Exception as e:
                results.append(f"Date analysis error for {col}: {str(e)}")
        
        return results
    
    def _analyze_statistics(self, df):
        """Provide statistical summary"""
        results = []
        
        # Basic statistics
        results.append(f"📊 Dataset shape: {df.shape[0]} rows × {df.shape[1]} columns")
        results.append(f"📊 Missing values: {df.isnull().sum().sum()} total")
        
        # Numeric statistics
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            results.append("📈 Numeric columns summary:")
            for col in numeric_cols[:3]:
                mean_val = df[col].mean()
                std_val = df[col].std()
                results.append(f"  • {col}: Mean = {mean_val:.2f}, Std = {std_val:.2f}")
        
        return results
    
    def _analyze_general(self, df):
        """General comprehensive analysis"""
        results = []
        
        results.append(f"📊 Dataset Overview: {df.shape[0]} rows, {df.shape[1]} columns")
        results.append(f"📊 Column types: {df.dtypes.value_counts().to_dict()}")
        
        # Top values in each column
        for col in df.columns[:3]:
            if df[col].dtype == 'object':
                top_val = df[col].value_counts().index[0] if len(df[col].value_counts()) > 0 else "None"
                results.append(f"🏷️ Most common in {col}: {top_val}")
        
        return results
    
    def _find_column(self, df, possible_names):
        """Find column by possible names"""
        for name in possible_names:
            for col in df.columns:
                if name.lower() in col.lower():
                    return col
        return None
    
    def _create_html_output(self, analysis_results):
        """Create HTML formatted output"""
        html = "<div style='font-family: Arial, sans-serif;'>"
        html += "<h2>📊 Analysis Results</h2>"
        
        for result in analysis_results:
            if result.startswith('📊') or result.startswith('📈') or result.startswith('👥'):
                html += f"<p><strong>{result}</strong></p>"
            elif result.startswith('  •'):
                html += f"<p style='margin-left: 20px;'>{result}</p>"
            else:
                html += f"<p>{result}</p>"
        
        html += "</div>"
        return html
    
    def _generate_analysis_code(self, df, user_query):
        """Generate executable Python code for the analysis"""
        code = f"""
# Generated code for analysis: {user_query}
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load the CSV file (update path as needed)
df = pd.read_csv('your_file.csv', encoding='utf-8')

# Basic information
print("📊 Dataset shape:", df.shape)
print("📊 Columns:", df.columns.tolist())
print("📊 Data types:")
print(df.dtypes)

# Analysis based on your query
"""

        query_lower = user_query.lower()
        
        if 'tweet' in query_lower and 'max' in query_lower:
            code += """
# Tweet analysis: Find max tweets per user per day
if 'user' in df.columns:
    # Find date column
    date_col = None
    for col in df.columns:
        if 'date' in col.lower():
            date_col = col
            break
    
    if date_col:
        # Convert to datetime and group
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df['date_only'] = df[date_col].dt.date
        
        # Count tweets per user per day
        daily_counts = df.groupby(['user', 'date_only']).size()
        max_tweets = daily_counts.max()
        
        print(f"📈 Maximum tweets per user per day: {max_tweets}")
        
        # Show top users
        max_users = daily_counts[daily_counts == max_tweets]
        print("👥 Users with maximum tweets:")
        for (user, date), count in max_users.head(10).items():
            print(f"  • {user} on {date}: {count} tweets")
"""
        else:
            code += """
# General analysis
# Show basic statistics
print("\\n📊 Basic Statistics:")
print(df.describe())

# Show value counts for categorical columns
categorical_cols = df.select_dtypes(include=['object']).columns
for col in categorical_cols[:2]:
    print(f"\\n🏷️ Top values in {col}:")
    print(df[col].value_counts().head())

# Show missing values
print("\\n⚠️ Missing values:")
print(df.isnull().sum())
"""
        
        code += "\n# Display first few rows\nprint(\"\\n📋 Sample data:\")\nprint(df.head())\n"
        return code
