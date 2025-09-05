import pandas as pd
import numpy as np
from datetime import datetime
import re
import os

class FreeDataProcessor:
    def __init__(self):
        """Initialize free data processing tools"""
        self.supported_formats = ['csv', 'xlsx', 'json', 'txt']
        print("✅ Free Data Processor initialized")
    
    def process_file(self, file_path):
        """Process different file formats without external APIs"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            file_extension = file_path.split('.')[-1].lower()
            
            if file_extension == 'csv':
                return self._process_csv(file_path)
            elif file_extension in ['xlsx', 'xls']:
                return self._process_excel(file_path)
            elif file_extension == 'json':
                return self._process_json(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _process_csv(self, file_path):
        """Process CSV files with comprehensive error handling"""
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'utf-16']
            df = None
            used_encoding = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding, low_memory=False)
                    used_encoding = encoding
                    print(f"✅ CSV loaded successfully with {encoding} encoding")
                    break
                except (UnicodeDecodeError, UnicodeError):
                    continue
                except Exception as e:
                    print(f"⚠️ Error with {encoding}: {str(e)}")
                    continue
            
            if df is None:
                raise ValueError("Could not decode CSV file with any standard encoding")
            
            # Clean and process the dataframe
            df = self._clean_dataframe(df)
            
            # Get detailed information
            info = self._get_detailed_info(df)
            info['encoding_used'] = used_encoding
            
            return {
                'success': True,
                'dataframe': df,
                'info': info,
                'processing_notes': self._get_processing_notes(df)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _process_excel(self, file_path):
        """Process Excel files"""
        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            df = self._clean_dataframe(df)
            
            return {
                'success': True,
                'dataframe': df,
                'info': self._get_detailed_info(df),
                'processing_notes': self._get_processing_notes(df)
            }
            
        except Exception as e:
            return {'success': False, 'error': f"Excel processing error: {str(e)}"}
    
    def _process_json(self, file_path):
        """Process JSON files"""
        try:
            df = pd.read_json(file_path)
            df = self._clean_dataframe(df)
            
            return {
                'success': True,
                'dataframe': df,
                'info': self._get_detailed_info(df),
                'processing_notes': self._get_processing_notes(df)
            }
            
        except Exception as e:
            return {'success': False, 'error': f"JSON processing error: {str(e)}"}
    
    def _clean_dataframe(self, df):
        """Comprehensive data cleaning"""
        original_shape = df.shape
        
        # Remove completely empty rows and columns
        df = df.dropna(how='all').dropna(axis=1, how='all')
        
        # Clean column names
        df.columns = [self._clean_column_name(col) for col in df.columns]
        
        # Handle duplicate columns
        df = self._handle_duplicate_columns(df)
        
        # Auto-detect and convert data types
        df = self._auto_convert_types(df)
        
        print(f"🧹 Data cleaned: {original_shape} → {df.shape}")
        return df
    
    def _clean_column_name(self, col_name):
        """Clean individual column names"""
        # Convert to string and strip whitespace
        clean_name = str(col_name).strip()
        
        # Remove special characters that might cause issues
        clean_name = re.sub(r'[^\w\s-]', '', clean_name)
        
        # Replace multiple spaces with single space
        clean_name = re.sub(r'\s+', ' ', clean_name)
        
        return clean_name
    
    def _handle_duplicate_columns(self, df):
        """Handle duplicate column names"""
        cols = pd.Series(df.columns)
        
        for dup in cols[cols.duplicated()].unique():
            cols[cols[cols == dup].index.values.tolist()] = [dup + '_' + str(i) if i != 0 else dup 
                                                             for i in range(sum(cols == dup))]
        
        df.columns = cols
        return df
    
    def _auto_convert_types(self, df):
        """Automatically convert data types"""
        for col in df.columns:
            # Try to convert date columns
            if self._looks_like_date(col) or self._contains_dates(df[col]):
                df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Try to convert numeric columns
            elif df[col].dtype == 'object':
                # Try converting to numeric
                numeric_series = pd.to_numeric(df[col], errors='coerce')
                if not numeric_series.isna().all():
                    non_null_count = numeric_series.count()
                    total_count = len(df[col])
                    if non_null_count / total_count > 0.8:  # If 80% can be converted
                        df[col] = numeric_series
        
        return df
    
    def _looks_like_date(self, column_name):
        """Check if column name suggests it contains dates"""
        date_indicators = ['date', 'time', 'created', 'updated', 'timestamp', 'birth', 'start', 'end']
        return any(indicator in column_name.lower() for indicator in date_indicators)
    
    def _contains_dates(self, series):
        """Check if series contains date-like strings"""
        if series.dtype != 'object':
            return False
        
        # Sample first few non-null values
        sample = series.dropna().head(10)
        if len(sample) == 0:
            return False
        
        date_count = 0
        for value in sample:
            try:
                pd.to_datetime(str(value))
                date_count += 1
            except:
                continue
        
        return date_count / len(sample) > 0.5
    
    def _get_detailed_info(self, df):
        """Get comprehensive information about the dataframe"""
        info = {
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
            'missing_values': df.isnull().sum().to_dict(),
            'missing_percentage': (df.isnull().sum() / len(df) * 100).round(2).to_dict(),
            'unique_counts': {col: df[col].nunique() for col in df.columns},
            'sample_data': df.head(3).to_dict('records')
        }
        
        # Add numeric statistics
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            info['numeric_summary'] = df[numeric_cols].describe().to_dict()
        
        # Add categorical information
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            info['categorical_info'] = {}
            for col in categorical_cols:
                value_counts = df[col].value_counts()
                info['categorical_info'][col] = {
                    'unique_values': len(value_counts),
                    'top_values': value_counts.head(5).to_dict()
                }
        
        # Add date information
        date_cols = df.select_dtypes(include=['datetime64[ns]']).columns
        if len(date_cols) > 0:
            info['date_info'] = {}
            for col in date_cols:
                info['date_info'][col] = {
                    'min_date': str(df[col].min()),
                    'max_date': str(df[col].max()),
                    'date_range_days': (df[col].max() - df[col].min()).days if df[col].notna().any() else 0
                }
        
        return info
    
    def _get_processing_notes(self, df):
        """Generate processing notes and recommendations"""
        notes = []
        
        # Check for high missing value columns
        missing_pct = (df.isnull().sum() / len(df) * 100)
        high_missing = missing_pct[missing_pct > 30]
        if len(high_missing) > 0:
            notes.append(f"⚠️ High missing values in: {list(high_missing.index)}")
        
        # Check for potential ID columns
        potential_ids = []
        for col in df.columns:
            if df[col].nunique() == len(df) and not df[col].isnull().any():
                potential_ids.append(col)
        if potential_ids:
            notes.append(f"🔍 Potential ID columns: {potential_ids}")
        
        # Check for low variance columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        low_variance = []
        for col in numeric_cols:
            if df[col].nunique() == 1:
                low_variance.append(col)
        if low_variance:
            notes.append(f"📊 Constant value columns: {low_variance}")
        
        # Check memory usage
        memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
        if memory_mb > 100:
            notes.append(f"💾 Large dataset: {memory_mb:.1f} MB in memory")
        
        # Data quality score
        total_cells = df.shape[0] * df.shape[1]
        missing_cells = df.isnull().sum().sum()
        quality_score = ((total_cells - missing_cells) / total_cells * 100) if total_cells > 0 else 0
        notes.append(f"✅ Data quality score: {quality_score:.1f}% (non-missing data)")
        
        return notes
